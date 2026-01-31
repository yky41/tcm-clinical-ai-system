from py2neo import Graph

# 连接到 Neo4j 数据库
graph = Graph("bolt://localhost:7687", auth=("neo4j", "12345678"))


def normalize_symptoms(user_responses):
    # Define a mapping of common symptoms to professional terms
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
        "月经":"带下"
        # Add more mappings as needed
    }
    normalized_responses = [symptom_mapping.get(response, response) for response in user_responses]
    return normalized_responses

# 查询中药信息的函数
class KBQA2:
    def query_medical_info(query_name):
        # 构建查询语句，根据用户输入的名称进行查询
        query = """
        MATCH (med:中药 {name: $name})-[:别名是]->(alias),
              (med)-[:气味品质是]->(smell),
              (med)-[:使用方法是]->(cure),
              (med)-[:属于]->(part)
        RETURN collect(distinct alias.name) AS 别名,
               collect(distinct smell.name) AS 气味,
               collect(distinct cure.name) AS 治疗方法,
               part.name AS 部位
        """
        # 执行查询
        result = graph.run(query, name=query_name).data()

        # 提取查询结果
        if result:
            medical_info = result[0]
            return medical_info
        else:
            return None


    # 匹配病情对应的治疗方法
    def match_cure_for_condition(condition):
        # 构建查询语句，匹配包含病情的治疗方法和别名
        query = """
        MATCH (med:中药 {name: $condition})
        RETURN med.cure AS 治疗方法,
        med.alias AS 别名
        """
        # 执行查询
        result = graph.run(query, condition=condition).data()

        if result:
            cure_and_alias = []
            for record in result:
                cure = record['治疗方法']
                alias = record['别名']
                # 检查治疗方法和别名是否为空，如果为空则不包含在返回结果中
                if cure is not None:
                    cure_and_alias.append(f"治疗方法: {cure}")
                if alias is not None:
                    cure_and_alias.append(f"别名: {alias}")
            return cure_and_alias
        else:
            return None

    # 记录用户的回答
    def filter_prescription_by_indications(user_responses):
        #user_responses = normalize_symptoms(user_responses)
        # 构建匹配查询语句，使用用户的回答去匹配 '主治' 属性中的内容
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
        LIMIT 1
        """

        # 执行查询
        result = graph.run(query, user_responses=user_responses).data()

        # 提取匹配度最高的药方
        if result:
            # 检查组成属性是否为空列表，如果是则设置为 None
            if not result[0]["组成"]:
                result[0]["组成"] = None
            return result[0]
        else:
            return None


    def match_cure_for_condition1(condition):
        # 构建查询语句，匹配包含病情的治疗方法以及对应的中药名字
        query = """
        MATCH (med:中药)-[:使用方法是]->(cure)
        WHERE cure.name CONTAINS $condition
        RETURN med.name AS 中药名字, cure.name AS 治疗方法
        LIMIT 5
        """
        # 执行查询
        result = graph.run(query, condition=condition).data()

        if result:
            # 逐条输出匹配结果
            output = ""
            for record in result:
                output += f"中药名字: {record['中药名字']}<br>"
                output += f"治疗方法: {record['治疗方法']}<br><br>"
            return output
        else:
            return None


if __name__ == "__main__":
    handler = KBQA1()
    while True:
        # 用户输入中药名或病情
        user_input = input("请输入中药名称或病情（输入 'exit' 退出）：")

        if user_input.lower() == 'exit':
            break

        # 查询中药信息
        medical_info = handler.query_medical_info(user_input)

        # 如果查询不到中药信息，尝试匹配病情对应的治疗方法
        if not medical_info:
            matched_cures = handler.match_cure_for_condition(user_input)
            if matched_cures:
                print("根据病情匹配的治疗方法是：")
                for cure in matched_cures:
                    print(cure)
            else:
                print("未找到相关信息。")
        else:
            # 输出查询结果
            print("别名:", medical_info['别名'])
            print("气味:", medical_info['气味'])
            print("治疗方法:")
            for cure in medical_info['治疗方法']:
                print(cure)
            print("所属部位:", medical_info['部位'])
