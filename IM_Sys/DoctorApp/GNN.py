import torch
import torch.nn.functional as F
from torch_geometric.nn import GCNConv
from torch_geometric.data import Data
from py2neo import Graph

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

class KBQA4:
    def __init__(self, db_url="bolt://localhost:7687", db_user="neo4j", db_password="12345678"):
        self.graph = Graph(db_url, auth=(db_user, db_password))
        self.device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
        self.model = GCN().to(self.device)
        self.optimizer = torch.optim.Adam(self.model.parameters(), lr=0.01)

    def normalize_symptoms(self, user_responses):
        symptom_mapping = {
            "受凉": "外感风寒",
        "发冷": "外感风寒",
        "流鼻涕": "外感风寒",
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
        "不": "",
        "无": "",
        "没有": "",
        "舌苔薄": "舌苔薄白",
        "舌苔白": "舌苔薄白",
        "出汗": "汗出恶风",
        "发汗": "汗出恶风",
        "冒虚汗": "汗出恶风",
        "疟疾": "症如疟状",
        "鼻子干": "鼻干",
        "鼻腔干": "鼻干",
        "大便异常": "便毒",
        "四肢疼": "肢体痛楚",
        "四肢痛": "肢体痛楚",
        "鼻子不通气": "鼻塞",
        "嗓子疼": "喉痹",
        "嗓子痛": "喉痹",
        "喉咙疼": "喉痹",
        "喉咙痛": "喉痹",
        "嗓子红": "咽喉淡红不肿",
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
        RETURN prescription.name AS 药方,
               indication.name AS 主治,
               prescription_type.name AS 方剂类型,
               usage.name AS 用法,
               collect(composition.name) AS 组成
        LIMIT 3
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
        x = torch.ones((len(nodes), 1))
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

    def predict_prescription(self, data, node_to_index, nodes, edges):
        max_confidence = -1
        max_prediction = None
        for node in nodes:
            if isinstance(node, str):
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
            if edge[0] == predicted_prescription and edge[1] != max_prediction and edge[1] != predicted_prescription:
                prescription_composition.append(edge[1])

        return max_prediction, predicted_prescription, prescription_composition, max_confidence

    def get_prescriptions(self, user_responses):
        normalized_responses = self.normalize_symptoms(user_responses)
        results = self.query_database(normalized_responses)

        if not results:
            return "未找到匹配的处方。"

        prescriptions = []
        for result in results:
            data, node_to_index, nodes, edges = self.build_graph_data([result])
            self.train_model(data)

            indication = normalized_responses[0]
            predicted_indication, predicted_prescription, prescription_composition, confidence = self.predict_prescription(
                data, node_to_index, nodes, edges)

            prescriptions.append({
                "预测症状": result["主治"],
                "预测处方": predicted_indication,
                "处方组成": result["组成"],
                "置信度": confidence,
                "方剂类型": result["方剂类型"],
                "用法": result["用法"]
            })

        # 格式化第一个匹配的处方以供 kbqa4 使用
        matched_prescription = prescriptions[0]
        prescription_info = {
            '药方': matched_prescription['预测处方'],
            '匹配度': matched_prescription['置信度'],
            '主治': matched_prescription['预测症状'],
            '方剂类型': matched_prescription['方剂类型'],
            '用法': matched_prescription['用法'],
            '组成': matched_prescription['处方组成']
        }

        return prescription_info


# 初始化和使用模型
kbqa = KBQA4()
user_responses = ["面色萎黄", "食积内停" ,"脘腹胀痛拒按"]
result = kbqa.get_prescriptions(user_responses)
# print(result)

# 保存模型
torch.save(kbqa.model.state_dict(), 'model.pth')

# 加载模型
kbqa.model.load_state_dict(torch.load('model.pth'))
