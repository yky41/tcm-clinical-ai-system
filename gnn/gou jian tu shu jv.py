import pandas as pd
import torch
from torch_geometric.data import Data
from py2neo import Graph

# Connect to your Neo4j database
graph = Graph("bolt://localhost:7687", auth=("neo4j", "12345678"))

# Fetch all nodes and relationships from the database
query = """
MATCH (prescription:方名)-[r]->(related_node)
RETURN prescription, r, related_node
"""
result = graph.run(query).data()

# Extract nodes and edges from the result
nodes = set()
edges = []
labels = []  # List to store labels

for record in result:
    prescription_name = record["prescription"]["name"]
    related_node_name = record["related_node"]["name"]
    relation_type = record["r"].type

    nodes.add(prescription_name)
    nodes.add(related_node_name)

    edges.append((prescription_name, related_node_name, relation_type))

    # Get labels
    label = 1 if prescription_name == related_node_name else 0
    labels.append(label)

# Map node names to unique indices
node_to_index = {node: index for index, node in enumerate(nodes)}

# Convert nodes and edges to PyTorch Geometric Data format
x = torch.eye(len(nodes))  # One-hot encode nodes
edge_index = [[node_to_index[src], node_to_index[dst]] for src, dst, _ in edges]
edge_index = torch.tensor(edge_index).t().contiguous()

# Convert edge types to edge labels
edge_attr = torch.tensor([0 for _ in range(len(edges))])  # Assuming all edges have the same label

# Convert labels to tensor
y = torch.tensor(labels)

# Create a PyTorch Geometric Data object
data = Data(x=x, edge_index=edge_index, edge_attr=edge_attr, y=y)

# Save graph data to disk using torch.save
torch.save(data, 'graph_data.pt')

print("Graph data saved successfully.")
