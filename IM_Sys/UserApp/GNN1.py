import torch
import torch.nn.functional as F
from torch_geometric.nn import GCNConv
from torch_geometric.data import Data
from py2neo import Graph

class KBQA5:
    def __init__(self, db_url="bolt://localhost:7687", db_user="neo4j", db_password="12345678", input_dim=16):
        self.graph = Graph(db_url, auth=(db_user, db_password))
        self.device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')

        # 初始化模型和优化器
        self.model = GCN(input_dim).to(self.device)
        self.optimizer = torch.optim.Adam(self.model.parameters(), lr=0.01)
        self.input_dim = input_dim  # 添加这一行来保存input_dim

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
            prescription_name = record["药方"]
            indication_name = record["主治"]
            prescription_type_name = record["方剂类型"]
            usage_name = record["用法"]
            composition_names = record["组成"].split(',')

            nodes.add(prescription_name)
            nodes.add(indication_name)
            nodes.add(prescription_type_name)
            nodes.add(usage_name)
            for composition_name in composition_names:
                nodes.add(composition_name.strip())

            edges.append((prescription_name, indication_name))
            edges.append((prescription_name, prescription_type_name))
            edges.append((prescription_name, usage_name))
            for composition_name in composition_names:
                edges.append((prescription_name, composition_name.strip()))

        node_to_index = {node: index for index, node in enumerate(nodes)}
        x = torch.ones((len(nodes), self.input_dim))  # 使用一个全为1的矩阵，形状为 (num_nodes, num_features)
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

    def predict_prescription(self, user_responses, top_k=3):
        if self.data is None:
            raise ValueError("Model has not been trained yet. Please train the model first.")

        normalized_responses = self.normalize_symptoms(user_responses)
        nodes_with_responses = [node for node in self.nodes if
                                isinstance(node, str) and any(response in node for response in normalized_responses)]

        predictions = []
        for index, node in enumerate(self.nodes):
            if node in nodes_with_responses:
                x = torch.zeros((1, len(self.nodes), self.input_dim))
                x[0, index] = torch.ones(self.input_dim)
                x = x.to(self.device)

                with torch.no_grad():
                    self.model.eval()
                    out = self.model(self.data)
                    pred_probability = out.squeeze()[index].item()

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
        top_predictions = predictions[:top_k]

        return top_predictions

    def get_prescription(self, user_responses):
        normalized_responses = self.normalize_symptoms(user_responses)
        result = self.query_database(normalized_responses)

        if not result:
            return "No matching prescription found."

        self.data, self.node_to_index, self.nodes, self.edges = self.build_graph_data(result)
        self.train_model(self.data)

        predicted_results = self.predict_prescription(user_responses)
        results = []
        for result in predicted_results:
            result_dict = {
                "预测症状": result[0],
                "预测处方": result[1],
                "处方组成": result[2],
                "置信度": result[3]
            }
            results.append(result_dict)
        return results


# 定义简单的图卷积网络 (GCN) 模型
class GCN(torch.nn.Module):
    def __init__(self, input_dim):
        super(GCN, self).__init__()
        self.conv1 = GCNConv(input_dim, 16)
        self.conv2 = GCNConv(16, 1)

    def forward(self, data):
        x, edge_index = data.x, data.edge_index

        x = self.conv1(x, edge_index)
        x = F.relu(x)
        x = F.dropout(x, training=self.training)

        x = self.conv2(x, edge_index)
        x = torch.sigmoid(x)

        return x

kbqa = KBQA5()

# 假设用户提供的症状列表
user_responses = ["外感风寒", "头疼", "发烧"]

# 获取预测结果
predicted_results = kbqa.get_prescription(user_responses)
for result in predicted_results:
    print("预测症状:", result["预测症状"])
    print("预测处方:", result["预测处方"])
    print("处方组成:", result["处方组成"])
    print("置信度:", result["置信度"])