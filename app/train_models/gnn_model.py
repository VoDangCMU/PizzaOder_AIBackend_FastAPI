import torch
import torch.nn as nn
from torch_geometric.nn import GCNConv
import torch.nn.functional as F

class GNNRecommendation(nn.Module):
    def __init__(self, in_dim, hidden_dim, out_dim, num_cat, num_ingr, num_shop):
        super().__init__()
        self.cat_emb = nn.Embedding(num_cat, 16)
        self.ingr_emb = nn.Embedding(num_ingr, 16)
        self.shop_emb = nn.Embedding(num_shop, 16)
        
        self.fuse_proj = nn.Linear(16 * 3, 24)

        self.gcn1 = GCNConv(in_dim + 24, hidden_dim)
        self.bn1 = nn.BatchNorm1d(hidden_dim)
        self.gcn2 = GCNConv(hidden_dim, out_dim)

    def forward(self, x, edge_index, cat_id, ingr_id, shop_id, edge_weight=None):
        cat_vec = self.cat_emb(cat_id)       # [num_nodes, 16]
        ingr_vec = self.ingr_emb(ingr_id)     # [num_nodes, 16]
        shop_vec = self.shop_emb(shop_id)     # [num_nodes, 16]
        
        print("cat_vec shape:", cat_vec.shape)
        print("ingr_vec shape:", ingr_vec.shape)
        print("shop_vec shape:", shop_vec.shape)
        fused_emb = torch.cat([cat_vec, ingr_vec, shop_vec], dim=1)  # [num_nodes, 48]
        fused_emb = F.relu(self.fuse_proj(fused_emb))                # [num_nodes, 24]

        x = torch.cat([x, fused_emb], dim=1)   # [num_nodes, in_dim + 24]

        # GCN layer 1
        x = self.gcn1(x, edge_index, edge_weight=edge_weight) # [num_nodes, hidden_dim]
        x = self.bn1(x)
        x = F.relu(x)

        # GCN layer 2
        x = self.gcn2(x, edge_index, edge_weight=edge_weight) # [num_nodes, out_dim]
        return x