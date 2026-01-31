import pandas as pd
from py2neo import Graph, Node, Relationship

# 连接到 Neo4j 数据库
graph = Graph("bolt://localhost:7687", auth=("neo4j", "12345678"))

# 读取 Excel 文件
df = pd.read_excel("清热剂.xlsx")

# 用于存储已创建节点的名称
created_nodes = {}

# 遍历 DataFrame 中的每一行
for index, row in df.iterrows():
    # 获取方剂类型、方名、组成、主治和用法
    prescription_type = row["方剂类型"]
    prescription_name = row["方名"]
    composition = row["组成"]
    indications = row["主治"]
    usage = row["用法"]

    prescription_type_node = created_nodes.get(prescription_type)
    if not prescription_type_node:
        prescription_type_node = Node("方剂类型", name=prescription_type)
        graph.create(prescription_type_node)
        created_nodes[prescription_type] = prescription_type_node


    # 尝试查找是否存在相同的方名节点
    prescription_node = created_nodes.get(prescription_name)
    if not prescription_node:
        prescription_node = Node('方名', name=prescription_name, 方剂类型=prescription_type)
        graph.create(prescription_node)
        created_nodes[prescription_name] = prescription_node

    # 尝试查找是否存在相同的组成节点
    composition_node = created_nodes.get(composition)
    if not composition_node:
        composition_node = Node("组成", name=composition)
        graph.create(composition_node)
        created_nodes[composition] = composition_node

    # 尝试查找是否存在相同的主治节点
    indications_node = created_nodes.get(indications)
    if not indications_node:
        indications_node = Node("主治", name=indications)
        graph.create(indications_node)
        created_nodes[indications] = indications_node

    # 尝试查找是否存在相同的用法节点
    usage_node = created_nodes.get(usage)
    if not usage_node:
        usage_node = Node("用法", name=usage)
        graph.create(usage_node)
        created_nodes[usage] = usage_node

    # 创建方名节点和关系节点之间的关系
    relation1 = Relationship(prescription_node, "COMPOSED_OF", composition_node)
    relation2 = Relationship(prescription_node, "INDICATED_FOR", indications_node)
    relation3 = Relationship(prescription_node, "USED_FOR", usage_node)
    relation4 = Relationship(prescription_type_node, "属于", prescription_node)
    graph.create(relation1)
    graph.create(relation2)
    graph.create(relation3)
    graph.create(relation4)
