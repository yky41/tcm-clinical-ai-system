import torch
import torch.nn.functional as F
from torch_geometric.nn import GCNConv
from torch_geometric.data import Data
from py2neo import Graph

class KBQA5:
    def __init__(self, db_url="bolt://localhost:7687", db_user="neo4j", db_password="12345678"):
        self.graph = Graph(db_url, auth=(db_user, db_password))
        self.device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
        self.model = None
        self.node_to_index = None
        self.nodes = None
        self.edges = None

    def normalize_symptoms(self, user_responses):
        symptom_mapping = {
            "受凉": "外感风寒",
            "发冷": "外感风寒",
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
            "流鼻子": "鼻流清涕",
            "流鼻涕": "鼻流清涕",
            "清鼻子": "鼻流清涕",
            "清鼻涕": "鼻流清涕",
            "腰酸背痛": "腰脊重痛",
            "不": "",
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
        AND prescription_type.name = '解表剂'
        RETURN prescription.name AS 药方,
               indication.name AS 主治,
               prescription_type.name AS 方剂类型,
               usage.name AS 用法,
               composition.name AS 组成
        """
        result = self.graph.run(query, user_responses=user_responses).data()
        return result

    def build_graph_data(self, result):
        nodes = set()
        edges = []

        for record in result:
            prescription_name = str(record["药方"])
            indication_name = str(record["主治"])
            composition_name = str(record["组成"])

            nodes.add(prescription_name)
            nodes.add(indication_name)
            nodes.add(composition_name)

            edges.append((prescription_name, composition_name))
            edges.append((prescription_name, indication_name))

        node_to_index = {node: index for index, node in enumerate(nodes)}
        self.node_to_index = node_to_index
        self.nodes = nodes
        self.edges = edges

        x = torch.eye(len(nodes))
        edge_index = [[node_to_index[str(src)], node_to_index[str(dst)]] for src, dst in edges]
        edge_index = torch.tensor(edge_index).t().contiguous()
        y = torch.zeros(len(nodes))
        for node in nodes:
            if node in [edge[0] for edge in edges]:
                y[node_to_index[str(node)]] = 1

        data = Data(x=x, edge_index=edge_index, y=y)
        return data

    def train_model(self, data):
        class GCN(torch.nn.Module):
            def __init__(self):
                super(GCN, self).__init__()
                self.conv1 = GCNConv(data.num_features, 16)
                self.conv2 = GCNConv(16, 1)

            def forward(self, data):
                x, edge_index = data.x, data.edge_index
                x = self.conv1(x, edge_index)
                x = F.relu(x)
                x = F.dropout(x, training=self.training)
                x = self.conv2(x, edge_index)
                x = torch.sigmoid(x)
                return x

        model = GCN().to(self.device)
        optimizer = torch.optim.Adam(model.parameters(), lr=0.01)

        model.train()
        for epoch in range(100):
            optimizer.zero_grad()
            out = model(data)
            loss = F.binary_cross_entropy(out.view(-1), data.y)
            loss.backward()
            optimizer.step()

        self.model = model

    def predict_prescription(self, user_responses, top_k=3):
        if not self.model:
            raise ValueError("Model has not been trained yet. Please train the model first.")

        normalized_responses = self.normalize_symptoms(user_responses)
        data = self.build_graph_data(self.query_database(normalized_responses))
        self.train_model(data)

        device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
        predictions = []
        for node in self.nodes:
            if isinstance(node, str) and any(response in node for response in normalized_responses):
                response_index = self.node_to_index[node]
                x = torch.zeros(len(self.nodes))
                x[response_index] = 1
                x = x.unsqueeze(0).to(device)
                with torch.no_grad():
                    self.model.eval()
                    out = self.model(data)
                    pred_probability = out.squeeze()[response_index].item()

                predicted_prescription = None
                for edge in self.edges:
                    if edge[1] == node:
                        predicted_prescription = edge[0]
                        break

                prescription_composition = []
                for edge in self.edges:
                    if edge[0] == predicted_prescription and edge[1] != predicted_prescription:
                        prescription_composition.append(edge[1])

                predictions.append((node, predicted_prescription, prescription_composition, pred_probability))

        predictions.sort(key=lambda x: x[3], reverse=True)
        return predictions[:top_k]

# 示例用法
kbqa = KBQA5()

user_responses = ["外感风寒", "头疼", "发烧"]
predicted_results = kbqa.predict_prescription(user_responses)
for result in predicted_results:
    print("预测症状:", result[0])
    print("预测处方:", result[1])
    print("处方组成:", result[2])
    print("置信度:", result[3])