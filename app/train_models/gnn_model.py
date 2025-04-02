import torch
import torch.nn as nn
from torch_geometric.nn import GCNConv

class GNNRecommendation(nn.Module):
    def __init__(self, in_dim, hidden_dim, out_dim, num_cat, num_ingr):
        super().__init__()
        self.cat_emb = nn.Embedding(num_cat, 8)
        self.ingr_emb = nn.Embedding(num_ingr, 8)
        self.gcn1 = GCNConv(in_dim + 16, hidden_dim)
        self.gcn2 = GCNConv(hidden_dim, out_dim)

    def forward(self, x, edge_index, cat_id, ingr_id, edge_weight=None):
        cat_vec = self.cat_emb(cat_id)
        ingr_vec = self.ingr_emb(ingr_id)
        x = torch.cat([x, cat_vec, ingr_vec], dim=1)
        x = torch.relu(self.gcn1(x, edge_index, edge_weight))
        return self.gcn2(x, edge_index, edge_weight)
