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
    model.eval() 
    return model
