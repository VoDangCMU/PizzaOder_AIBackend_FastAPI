# app/routers/recommender.py
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from app.train_models.load_model import load_model  
from app.postgresql.postgresql_config import SessionLocal  
from app.models.models import PizzaSale
from sklearn.preprocessing import LabelEncoder
import torch
import pandas as pd
from sklearn.metrics.pairwise import cosine_similarity
from app.utils.prepare_vector import prepare_node_features, prepare_edges, suggest_pizza_based_on_gnn_with_time
from sklearn.metrics.pairwise import cosine_similarity
router = APIRouter()

# class PizzaRecommendationRequest(BaseModel):
#     pizza_id: str 
#     order_time: str 
#     time_window: int  

device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
model = load_model(device)

def get_pizza_data():
    db = SessionLocal()
    try:
        pizzas = db.query(PizzaSale).all()
        pizza_data = pd.DataFrame([{
            'order_id': pizza.order_id,
            'pizza_name_id': pizza.pizza_name_id,
            'pizza_name': pizza.pizza_name,
            'pizza_category': pizza.pizza_category,
            'pizza_ingredients': pizza.pizza_ingredients,
            'order_date': pizza.order_date,
            'order_time': pizza.order_time,
            'quantity': pizza.quantity,
            'total_price': pizza.total_price,
            'pizza_size': pizza.pizza_size
        } for pizza in pizzas])
        return pizza_data
    except Exception as e:
        print(f"Error retrieving data: {e}")
        return []
    finally:
        db.close()

# @router.post("/recommend")
# async def recommend_pizza(request: PizzaRecommendationRequest):
#     device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
#     model, node_features, category_tensor, ingredient_tensor, edge_index, edge_weight = load_model(device)

#     pizza_data = get_pizza_data()

#     if pizza_data.empty:
#         raise HTTPException(status_code=404, detail="No pizza data found")

#     pizza_ids = pizza_data['pizza_name_id'].unique().tolist()
#     pizza_index_map = {pid: idx for idx, pid in enumerate(pizza_ids)}

#     suggested_pizza_ids = suggest_pizza_based_on_gnn_with_time(
#         pizza_id=request.pizza_id,
#         order_time=request.order_time,
#         time_window=request.time_window,
#         model=model,
#         node_features=node_features,
#         category_tensor=category_tensor,
#         ingredient_tensor=ingredient_tensor,
#         edge_index=edge_index,
#         edge_weight=edge_weight,
#         pizza_index_map=pizza_index_map,
#         pizza_ids=pizza_ids,
#         pizza_order_times=pizza_data['order_time'].tolist()
#     )

#     if not suggested_pizza_ids:
#         raise HTTPException(status_code=404, detail="No similar pizzas found")

#     return {"suggested_pizza_ids": suggested_pizza_ids}

class PizzaRecommendationRequest(BaseModel):
    pizza_id: str 
    order_time: str 
    time_window: int  
    day: int
    month: int
    weekday: int
    shop_name: str

def time_to_minutes(t):
    t = pd.to_datetime(t, format='%H:%M:%S')
    return t.hour * 60 + t.minute

def suggest_pizza_based_on_gnn_with_time1(
    pizza_id, order_time, time_window, pizza_index_map,
    model, node_features, category_tensor, ingredient_tensor, edge_index, edge_weight,
    pizza_ids, pizza_order_times, shop_tensor, top_n=6
):
    pizza_idx = pizza_index_map.get(pizza_id, None)
    if pizza_idx is None:
        print(f"Pizza ID {pizza_id} không có trong bản đồ pizza.")
        return []

    order_time_minutes = time_to_minutes(order_time)
    window_start = order_time_minutes - time_window
    window_end = order_time_minutes + time_window

    pizza_embeddings = model(node_features, edge_index, category_tensor, ingredient_tensor, shop_tensor, edge_weight)
    pizza_embedding = pizza_embeddings[pizza_idx]

    similarity_scores = []
    for i, emb in enumerate(pizza_embeddings):
        if pizza_ids[i] != pizza_id:  # Loại bỏ pizza_id chính mình
            pizza_time = pizza_order_times[i]
            pizza_time_minutes = time_to_minutes(pizza_time)

            if window_start <= pizza_time_minutes <= window_end:
                similarity = cosine_similarity(pizza_embedding.unsqueeze(0).cpu().detach().numpy(), emb.unsqueeze(0).cpu().detach().numpy())[0][0]
                similarity_scores.append((pizza_ids[i], similarity))

    similarity_scores.sort(key=lambda x: x[1], reverse=True)
    top_pizzas = similarity_scores[:top_n]

    return top_pizzas


@router.post("/recommend")
async def recommend_pizza(request: PizzaRecommendationRequest):
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    model, node_features, category_tensor, ingredient_tensor, edge_index, edge_weight, pizza_index_map, pizza_ids, order_times, shop_tensor = load_model(device)
    print('2',shop_tensor.shape)
    


    suggested_pizza_ids = suggest_pizza_based_on_gnn_with_time1(
        pizza_id=request.pizza_id,
        order_time=request.order_time,
        time_window=request.time_window,
        # day= request.day,
        # month= request.month,
        # weekday= request.weekday,
        # shop_name= request.shop_name,
        model=model,
        node_features=node_features,
        category_tensor=category_tensor,
        ingredient_tensor=ingredient_tensor,
        edge_index=edge_index,
        edge_weight=edge_weight,
        pizza_index_map=pizza_index_map,
        pizza_ids=pizza_ids,
        pizza_order_times = order_times,
        shop_tensor=shop_tensor
    )

    if not suggested_pizza_ids:
        raise HTTPException(status_code=404, detail="No similar pizzas found")

    return {
    "suggested_pizza_ids": [
        (pizza_id, float(score)) for pizza_id, score in suggested_pizza_ids
    ]
    }

