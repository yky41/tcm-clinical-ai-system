from py2neo import Graph

# 连接到 Neo4j 数据库
graph = Graph("bolt://localhost:7687", auth=("neo4j", "12345678"))


def normalize_symptoms(user_responses):
    # Define a mapping of common symptoms to professional terms
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
        "流鼻涕": "鼻流",
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
        "嗓子疼": "咽喉淡红不肿",
        "嗓子痛": "咽喉淡红不肿",


        "积食": "食积",
        "肚子胀气": "脘腹胀闷",
        "喝乳制品": "乳食积滞",
        "喝乳制品了": "乳食积滞",
        "肚子胀": "腹部胀实",
        "肚子疼": "脘腹胀痛",
        "肚子痛": "脘腹胀痛",
        "胁肋部疼": "引胁肋痛",
        "胁肋部痛": "引胁肋痛",
        "后背疼": "痛连背膂",
        "反胃酸": "吞酸",
        "按压肚子疼": "脘腹胀痛拒按",
        "厌食": "恶食",
        "便秘": "大便秘结",
        "有蛔虫": "蛔虫积于肠道",
        "大便臭": "粪便臭如败卵",
        "大便不通畅": "泻而不爽",
        "胃疼": "脘痞胀痛",
        "胃痛": "脘痞胀痛",
        "胃胀": "脘痞胀痛",
        "胃": "脘痞",
        "暴饮暴食": "饮食过多",
        "消化不好": "难消",
        "大便稀": "大便溏薄",
        "面色黄": "面色萎黄",
        "打嗝有腐臭味": "嗳腐",



        # Add more mappings as needed
    }
    normalized_responses = [symptom_mapping.get(response, response) for response in user_responses]
    return normalized_responses

# 查询中药信息的函数
class KBQA1:
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
        OPTIONAL MATCH (med)-[:使用方法是]->(cure:主治方法)
        OPTIONAL MATCH (med)-[:别名是]->(alias:别名)
        RETURN med.name AS 药材名字, cure.name AS 治疗方法, alias.name AS 别名
        """
        # 执行查询
        result = graph.run(query, condition=condition).data()

        if result:
            cure_and_alias = []
            for record in result:
                med_name = record['药材名字']
                cure = record['治疗方法']
                alias = record['别名']
                # 添加药材名字
                if med_name:
                    cure_and_alias.append(f"药材名字: {med_name}")
                # 检查治疗方法和别名是否为空，如果为空则不包含在返回结果中
                if cure:
                    cure_and_alias.append(f"治疗方法: {cure}")
                if alias:
                    cure_and_alias.append(f"别名: {alias}")
            # 将不同部分用段落分隔
            return "<br>".join(cure_and_alias)
        else:
            return None

    # 记录用户的回答
    def filter_prescription_by_indications(user_responses):
        user_responses = normalize_symptoms(user_responses)
        print(user_responses)  # 调试输出用户的症状列表

        prescriptions = []

        for i in range(len(user_responses), 0, -1):
            current_responses = user_responses[:i]

            if "感冒" in user_responses:
                query = """
                MATCH (prescription:方名)-[:主治]->(indication)
                MATCH (prescription)-[:组成]->(composition)
                MATCH (prescription)-[:方剂类型]->(prescription_type)
                MATCH (prescription)-[:用法]->(usage)
                WHERE ANY(response IN $current_responses WHERE indication.name =~ '(?i).*' + response + '.*')
                  AND prescription_type.name = "解表剂"
                RETURN prescription.name AS 药方,
                       COLLECT(indication.name) AS 主治,
                       prescription_type.name AS 方剂类型,
                       usage.name AS 用法,
                       COLLECT(composition.name) AS 组成
                
                """
            elif "消化不良" in user_responses:
                query = """
                MATCH (prescription:方名)-[:主治]->(indication)
                MATCH (prescription)-[:组成]->(composition)
                MATCH (prescription)-[:方剂类型]->(prescription_type)
                MATCH (prescription)-[:用法]->(usage)
                WHERE ANY(response IN $current_responses WHERE indication.name =~ '(?i).*' + response + '.*')
                  AND prescription_type.name = "消导剂"
                RETURN prescription.name AS 药方,
                       COLLECT(indication.name) AS 主治,
                       prescription_type.name AS 方剂类型,
                       usage.name AS 用法,
                       COLLECT(composition.name) AS 组成
                
                """
            else:
                query = """
                MATCH (prescription:方名)-[:主治]->(indication)
                MATCH (prescription)-[:组成]->(composition)
                MATCH (prescription)-[:方剂类型]->(prescription_type)
                MATCH (prescription)-[:用法]->(usage)
                WHERE ANY(response IN $current_responses WHERE indication.name =~ '(?i).*' + response + '.*')
                RETURN prescription.name AS 药方,
                       COLLECT(indication.name) AS 主治,
                       prescription_type.name AS 方剂类型,
                       usage.name AS 用法,
                       COLLECT(composition.name) AS 组成
                
                """

            print(f"Executing query with current_responses: {current_responses}")  # 调试输出当前的查询条件
            result = graph.run(query, current_responses=current_responses).data()

            if result:
                for item in result:
                    matched_symptoms = [response for response in current_responses if
                                        any(response in indication for indication in item["主治"])]
                    if matched_symptoms:
                        prescription = {
                            "药方": item["药方"],
                            "主治": ", ".join(item["主治"]),
                            "方剂类型": item["方剂类型"],
                            "用法": item["用法"],
                            "组成": ", ".join(item["组成"]) if item["组成"] else None,
                            "匹配病症": ", ".join(matched_symptoms)
                        }
                        prescriptions.append(prescription)
                if prescriptions:
                    break  # 找到匹配的药方后退出循环

        # 按照匹配症状数量对药方进行排序
        prescriptions.sort(key=lambda x: len(x["匹配病症"].split(", ")), reverse=True)

        return prescriptions if prescriptions else None

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
