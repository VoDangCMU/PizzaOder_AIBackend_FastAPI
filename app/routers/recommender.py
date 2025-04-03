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

router = APIRouter()

class PizzaRecommendationRequest(BaseModel):
    pizza_id: str 
    order_time: str 
    time_window: int  

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

@router.post("/recommend")
async def recommend_pizza(request: PizzaRecommendationRequest):
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    model, node_features, category_tensor, ingredient_tensor, edge_index, edge_weight = load_model(device)

    pizza_data = get_pizza_data()

    if pizza_data.empty:
        raise HTTPException(status_code=404, detail="No pizza data found")

    pizza_ids = pizza_data['pizza_name_id'].unique().tolist()
    pizza_index_map = {pid: idx for idx, pid in enumerate(pizza_ids)}

    suggested_pizza_ids = suggest_pizza_based_on_gnn_with_time(
        pizza_id=request.pizza_id,
        order_time=request.order_time,
        time_window=request.time_window,
        model=model,
        node_features=node_features,
        category_tensor=category_tensor,
        ingredient_tensor=ingredient_tensor,
        edge_index=edge_index,
        edge_weight=edge_weight,
        pizza_index_map=pizza_index_map,
        pizza_ids=pizza_ids,
        pizza_order_times=pizza_data['order_time'].tolist()
    )

    if not suggested_pizza_ids:
        raise HTTPException(status_code=404, detail="No similar pizzas found")

    return {"suggested_pizza_ids": suggested_pizza_ids}
