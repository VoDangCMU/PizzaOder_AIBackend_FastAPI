import torch
import numpy as np
from collections import Counter
from sklearn.metrics.pairwise import cosine_similarity
import pandas as pd

def time_to_minutes(t):
    """Chuyển thời gian order thành số phút trong ngày."""
    t = pd.to_datetime(t, format='%H:%M:%S')
    return t.hour * 60 + t.minute

def suggest_pizza_based_on_gnn_with_time(pizza_id, order_time, time_window, model, node_features, category_tensor, ingredient_tensor, edge_index, edge_weight, pizza_index_map, pizza_ids, pizza_order_times, top_n=5):
    """
    Gợi ý các pizza tương tự dựa trên mô hình GNN đã huấn luyện và thời gian order.
    Trả về danh sách top N pizza_name_id có độ tương đồng cao với pizza_id được chọn và trong phạm vi thời gian gần với order_time.
    """
    
    pizza_idx = pizza_index_map.get(pizza_id, None)
    if pizza_idx is None:
        print(f"Pizza ID {pizza_id} không có trong bản đồ pizza.")
        return []

    user_time_in_minutes = time_to_minutes(order_time)

    time_range_min = user_time_in_minutes - time_window
    time_range_max = user_time_in_minutes + time_window
    
    pizza_ids_in_time_range = [pid for pid, p_time in zip(pizza_ids, pizza_order_times) if time_range_min <= time_to_minutes(p_time) <= time_range_max]

    if pizza_id not in pizza_ids_in_time_range:
        pizza_ids_in_time_range.append(pizza_id) 

    pizza_embedding = model(node_features, edge_index, category_tensor, ingredient_tensor, edge_weight)[pizza_idx].detach().cpu().numpy()

    all_embeddings = model(node_features, edge_index, category_tensor, ingredient_tensor, edge_weight).detach().cpu().numpy()

    similarities = cosine_similarity([pizza_embedding], all_embeddings)[0]

    similar_pizza_indices = [idx for idx, pid in enumerate(pizza_ids) if pid in pizza_ids_in_time_range]
    
    similar_pizza_indices = sorted(similar_pizza_indices, key=lambda x: similarities[x], reverse=True)
    
    similar_pizza_ids = [pizza_ids[idx] for idx in similar_pizza_indices[:top_n]]

    return similar_pizza_ids

def prepare_node_features(pizza_data):
    features, categories, ingredients = [], [], []
    for _, row in pizza_data.iterrows():
        size = torch.tensor(row[['S','M','L','XL','XXL']].astype(float).values, dtype=torch.float32)
        q = torch.tensor([row['quantity']], dtype=torch.float32)
        p = torch.tensor([row['total_price']], dtype=torch.float32)
        t = torch.tensor(time_to_vec(row['order_time']), dtype=torch.float32)
        feat = torch.cat([size, q, p, t])
        features.append(feat)
        categories.append(row['pizza_category_encoded'])
        ingredients.append(row['pizza_ingredients_encoded'])
    
    node_features = torch.stack(features).float()
    category_tensor = torch.tensor(categories, dtype=torch.long)
    ingredient_tensor = torch.tensor(ingredients, dtype=torch.long)

    return node_features, category_tensor, ingredient_tensor

def prepare_edges(pizza_data):
    pizza_ids = pizza_data['pizza_name_id'].unique().tolist()
    pizza_index_map = {pid: idx for idx, pid in enumerate(pizza_ids)}

    edge_pairs = []
    for _, g in pizza_data.groupby("order_id"):
        ids = g.sort_values("order_time")['pizza_name_id'].tolist()
        for i in range(len(ids)-1):
            pair = (pizza_index_map[ids[i]], pizza_index_map[ids[i+1]])
            edge_pairs.append(pair)

    pair_counter = Counter(edge_pairs)
    edge_index = torch.tensor(list(pair_counter.keys()), dtype=torch.long).t().contiguous()
    edge_weight = torch.tensor(list(pair_counter.values()), dtype=torch.float32)

    return edge_index, edge_weight, pizza_index_map, pizza_ids

def time_to_vec(t):
    """Chuyển thời gian thành vector (sin, cos) cho việc sử dụng trong mô hình GNN."""
    t = pd.to_datetime(t, format='%H:%M:%S')
    h = t.hour + t.minute / 60
    return [np.sin(2*np.pi*h/24), np.cos(2*np.pi*h/24)]
