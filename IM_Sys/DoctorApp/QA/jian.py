from py2neo import Graph, Node, Relationship

class PrescriptionSaver:
    def __init__(self, uri, user, password):
        self.graph = Graph(uri, auth=(user, password))

    def save_prescription(self, prescription):
        try:
            prescription_type = prescription["方剂类型"]
            prescription_name = prescription["方名"]
            composition = prescription["组成"]
            indications = prescription["主治"]
            usage = prescription.get("用法", "")

            prescription_type_node = self.graph.nodes.match("方剂类型", name=prescription_type).first()
            if not prescription_type_node:
                prescription_type_node = Node("方剂类型", name=prescription_type)
                self.graph.create(prescription_type_node)

            prescription_node = self.graph.nodes.match("方名", name=prescription_name).first()
            if not prescription_node:
                prescription_node = Node('方名', name=prescription_name, 方剂类型=prescription_type)
                self.graph.create(prescription_node)

            composition_node = self.graph.nodes.match("组成", name=composition).first()
            if not composition_node:
                composition_node = Node("组成", name=composition)
                self.graph.create(composition_node)

            indications_node = self.graph.nodes.match("主治", name=indications).first()
            if not indications_node:
                indications_node = Node("主治", name=indications)
                self.graph.create(indications_node)

            usage_node = self.graph.nodes.match("用法", name=usage).first()
            if not usage_node:
                usage_node = Node("用法", name=usage)
                self.graph.create(usage_node)

            prescription_node["方剂类型"] = prescription_type
            self.graph.push(prescription_node)

            relation1 = Relationship(prescription_node, "组成", composition_node)
            relation2 = Relationship(prescription_node, "主治", indications_node)
            relation3 = Relationship(prescription_node, "用法", usage_node)
            relation4 = Relationship(prescription_node, "方剂类型", prescription_type_node)

            self.graph.merge(relation1)
            self.graph.merge(relation2)
            self.graph.merge(relation3)
            self.graph.merge(relation4)

            print(f"Prescription {prescription_name} saved successfully.")
        except Exception as e:
            print(f"Error saving prescription: {e}")