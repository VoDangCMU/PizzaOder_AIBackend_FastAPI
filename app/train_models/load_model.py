import torch
from app.train_models.gnn_model import GNNRecommendation

def load_model(device):
    """Hàm load mô hình GNN đã lưu từ thư mục models"""
    
    model = GNNRecommendation(
        in_dim=9,  
        hidden_dim=64,
        out_dim=32,
        num_cat=4,
        num_ingr=32  
    ).to(device)

    model.load_state_dict(torch.load("app/train_models/gnn_recommendation_model1.pth"), strict=False)
    
    node_features = torch.load("app/train_models/node_features.pth").to(device)
    category_tensor = torch.load("app/train_models/category_tensor.pth").to(device)
    ingredient_tensor = torch.load("app/train_models/ingredient_tensor.pth").to(device)
    edge_index = torch.load("app/train_models/edge_index.pth").to(device)
    edge_weight = torch.load("app/train_models/edge_weight.pth").to(device)

    model.eval() 
    
    return model, node_features, category_tensor, ingredient_tensor, edge_index, edge_weight
