import torch
import torch.nn.functional as F
from torch_geometric.nn import GCNConv
from torch_geometric.data import Data
from py2neo import Graph

class TCM:
    def __init__(self, db_url="bolt://localhost:7687", db_user="neo4j", db_password="12345678"):
        self.graph = Graph(db_url, auth=(db_user, db_password))
        self.device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')

        # 初始化模型和优化器
        self.model = GCN().to(self.device)
        self.optimizer = torch.optim.Adam(self.model.parameters(), lr=0.01)

    def normalize_symptoms(self, user_responses):
        symptom_mapping = {
            "受凉": "外感风寒",
            "发冷": "外感风寒",
            "流鼻涕": "外感风寒",
            "喉咙痛": "外感风寒",
            "打喷嚏": "外感风寒",
            "觉得冷": "恶寒",
            "发烧": "发热",
            "头疼": "头痛",
            "小孩": "小儿",
            "孩子": "小儿",
            "娃娃": "小儿",
            "眼睛疼": "目痛",
            "浑身疼": "身疼",
            "浑身痛": "身疼",
            "皮疹": "荨麻疹",
            "疹子": "荨麻疹",
            "嘴唇干": "唇焦",
            "时冷时热": "寒热交作",
            "忽冷忽热": "寒热交作",
            "一会冷一会热": "寒热交作",
            "有痰": "痰",
            "流鼻子": "鼻流",
            "清鼻子": "清涕",
            "清鼻涕": "清涕",
            "腰酸背痛": "腰脊重痛",
        }
        normalized_responses = [symptom_mapping.get(response, response) for response in user_responses]
        return normalized_responses

    def query_database(self, user_responses):
        query = """
        MATCH (prescription:方名)-[:主治]->(indication)
        MATCH (prescription)-[:组成]->(composition)
        MATCH (prescription)-[:方剂类型]->(prescription_type)
        MATCH (prescription)-[:用法]->(usage)
        WHERE ANY(response IN $user_responses WHERE indication.name CONTAINS response)
        {condition}
        RETURN prescription.name AS 药方,
               indication.name AS 主治,
               prescription_type.name AS 方剂类型,
               usage.name AS 用法,
               collect(composition.name) AS 组成
        LIMIT 1
        """

        if user_responses[0] == "外感风寒":
            query = query.format(condition="AND prescription_type.name = '解表剂'")
        else:
            query = query.format(condition="")

        result = self.graph.run(query, user_responses=user_responses).data()
        return result

    def build_graph_data(self, result):
        nodes = set()
        edges = []

        for record in result:
            prescription_name = record["药方"]
            indication_name = record["主治"]
            prescription_type_name = record["方剂类型"]
            usage_name = record["用法"]
            composition_names = record["组成"]

            nodes.add(prescription_name)
            nodes.add(indication_name)
            nodes.add(prescription_type_name)
            nodes.add(usage_name)
            for composition_name in composition_names:
                nodes.add(composition_name)

            edges.append((prescription_name, indication_name))
            edges.append((prescription_name, prescription_type_name))
            edges.append((prescription_name, usage_name))
            for composition_name in composition_names:
                edges.append((prescription_name, composition_name))

        node_to_index = {node: index for index, node in enumerate(nodes)}
        x = torch.ones((len(nodes), 1))  # 使用一个全为1的矩阵，形状为 (num_nodes, num_features)
        edge_index = [[node_to_index[src], node_to_index[dst]] for src, dst in edges]
        edge_index = torch.tensor(edge_index).t().contiguous()

        y = torch.zeros(len(nodes))
        for node in nodes:
            if node in [edge[0] for edge in edges]:
                y[node_to_index[node]] = 1

        data = Data(x=x, edge_index=edge_index, y=y)
        return data, node_to_index, nodes, edges

    def train_model(self, data):
        self.model.train()
        for epoch in range(100):
            self.optimizer.zero_grad()
            out = self.model(data)
            loss = F.binary_cross_entropy(out.view(-1), data.y)
            loss.backward()
            self.optimizer.step()

    def predict_prescription(self, indication, data, node_to_index, nodes, edges):
        nodes_with_indication = [node for node in nodes if isinstance(node, str) and indication in node]

        max_confidence = -1
        max_prediction = None
        for node in nodes_with_indication:
            indication_index = node_to_index[node]
            x = torch.zeros(len(nodes))
            x[indication_index] = 1
            x = x.unsqueeze(0).to(self.device)

            with torch.no_grad():
                self.model.eval()
                out = self.model(data)
                pred_probability = out.squeeze()[indication_index].item()

            if pred_probability > max_confidence:
                max_confidence = pred_probability
                max_prediction = node

        predicted_prescription = None
        for edge in edges:
            if edge[1] == max_prediction:
                predicted_prescription = edge[0]
                break

        prescription_composition = []
        for edge in edges:
            if edge[0] == predicted_prescription and edge[1] != indication and edge[1] != predicted_prescription:
                prescription_composition.append(edge[1])

        return max_prediction, predicted_prescription, prescription_composition, max_confidence

    def get_prescription(self, user_responses):
        normalized_responses = self.normalize_symptoms(user_responses)
        result = self.query_database(normalized_responses)

        if not result:
            return "No matching prescription found."

        data, node_to_index, nodes, edges = self.build_graph_data(result)
        self.train_model(data)

        indication = normalized_responses[0]
        predicted_indication, predicted_prescription, prescription_composition, confidence = self.predict_prescription(
            indication, data, node_to_index, nodes, edges)

        return {
            "预测症状": predicted_indication,
            "预测处方": predicted_prescription,
            "处方组成": result[0]["组成"],
            "置信度": confidence,
            "方剂类型": result[0]["方剂类型"],
            "用法": result[0]["用法"]
        }

# 定义简单的图卷积网络 (GCN) 模型
class GCN(torch.nn.Module):
    def __init__(self):
        super(GCN, self).__init__()
        self.conv1 = GCNConv(1, 16)
        self.conv2 = GCNConv(16, 1)

    def forward(self, data):
        x, edge_index = data.x, data.edge_index

        x = self.conv1(x, edge_index)
        x = F.relu(x)
        x = F.dropout(x, training=self.training)

        x = self.conv2(x, edge_index)
        x = torch.sigmoid(x)

        return x
