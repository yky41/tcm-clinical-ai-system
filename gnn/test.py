import torch

# Load graph data
data = torch.load('graph_data.pt')

# Check if labels are present
if data.y is not None:
    print("Labels are present in the graph data.")
    print("Shape of labels:", data.y.shape)
else:
    print("Labels are not present in the graph data.")
