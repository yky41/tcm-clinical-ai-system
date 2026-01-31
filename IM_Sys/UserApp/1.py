import pandas as pd
from py2neo import Graph, Node, Relationship

# 连接到 Neo4j 数据库
graph = Graph("bolt://localhost:7687", auth=("neo4j", "12345678"))

# 读取 Excel 文件
df = pd.read_excel("部.xlsx")

# 遍历 DataFrame 中的每一行
for index, row in df.iterrows():
    # 获取方剂类型、方名、组成、主治和用法
    prescription_type = row["方剂类型"]
    prescription_name = row["方名"]
    composition = row["组成"]
    indications = row["主治"]
    usage = row["用法"]

    # 尝试查找是否存在相同名称的节点
    existing_node = graph.nodes.match("方名", name=prescription_name).first()
    if existing_node:
        prescription_node = existing_node
    else:
        prescription_node = Node('方名', name=prescription_name, 方剂类型=prescription_type)
        graph.create(prescription_node)

    # 尝试查找是否存在相同名称的组成节点
    if composition:  # 检查组成属性是否为空
        existing_composition_node = graph.nodes.match("组成", name=composition).first()
        if not existing_composition_node:
            composition_node = Node("组成", name=composition)
            graph.create(composition_node)
        else:
            composition_node = existing_composition_node
        # 创建方名节点和组成节点之间的关系
        relation1 = Relationship(prescription_node, "组成", composition_node)
        graph.create(relation1)

    # 尝试查找是否存在相同名称的主治节点
    existing_indications_node = graph.nodes.match("主治", name=indications).first()
    if not existing_indications_node:
        indications_node = Node("主治", name=indications)
        graph.create(indications_node)
    else:
        indications_node = existing_indications_node
    # 创建方名节点和主治节点之间的关系
    relation2 = Relationship(prescription_node, "主治", indications_node)
    graph.create(relation2)

    # 尝试查找是否存在相同名称的用法节点
    existing_usage_node = graph.nodes.match("用法", name=usage).first()
    if not existing_usage_node:
        usage_node = Node("用法", name=usage)
        graph.create(usage_node)
    else:
        usage_node = existing_usage_node
    # 创建方名节点和用法节点之间的关系
    relation3 = Relationship(prescription_node, "用法", usage_node)
    graph.create(relation3)

    # 尝试查找是否存在相同名称的方剂类型节点
    existing_type_node = graph.nodes.match("方剂类型", name=prescription_type).first()
    if not existing_type_node:
        type_node = Node("方剂类型", name=prescription_type)
        graph.create(type_node)
    else:
        type_node = existing_type_node
    # 创建方名节点和方剂类型节点之间的关系
    relation4 = Relationship(prescription_node, "方剂类型", type_node)
    graph.create(relation4)
