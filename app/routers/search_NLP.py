import openai
import os
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from app.postgresql.postgresql_config import SessionLocal
from app.models.models import PizzaSale
from openai import OpenAI 
import re

apikey = os.getenv("api_key")  
client = OpenAI(api_key=apikey)

router = APIRouter()

class QueryRequest(BaseModel):
    query: str  

def get_pizza_data(size=None, money=None, category=None, ingredients=None, target_price=None):
    db = SessionLocal()
    query = db.query(PizzaSale).distinct() 

    if size:
        query = query.filter(PizzaSale.pizza_size.ilike(f"%{size}%"))
    if category:
        query = query.filter(PizzaSale.pizza_category.ilike(f"%{category}%"))
    if ingredients:
        ingredients = ingredients.replace(" ", ",")
        
        for ingredient in ingredients.split(','):
            query = query.filter(PizzaSale.pizza_ingredients.ilike(f"%{ingredient}%"))

    
    if target_price:
        lower_bound = target_price * 0.9
        upper_bound = target_price * 1.1
        query = query.filter(PizzaSale.unit_price.between(lower_bound, upper_bound))

    pizzas = query.all()
    return pizzas

def extract_entities_from_query(query: str):
    """
    Sử dụng OpenAI API để nhận diện các thực thể size, money, category và ingredients.
    """
    
    prompt = f"""
    From the following query, identify the size only(S, M, L, XL, XXL), money only (low, medium, hight), category only (Classic, Veggie, Supreme, Chicken), and ingredients only ('?duja Salami', 'Alfredo Sauce', 'Anchovies', 'Artichoke', 'Artichokes', 'Arugula', 'Asiago Cheese', 'Bacon', 'Barbecue Sauce', 'Barbecued Chicken', 'Beef Chuck Roast', 'Blue Cheese', 'Brie Carre Cheese', 'Calabrese Salami', 'Capocollo', 'Caramelized Onions', 'Chicken', 'Chipotle Sauce', 'Chorizo Sausage', 'Cilantro', 'Coarse Sicilian Salami', 'Corn', 'Eggplant', 'Feta Cheese', 'Fontina Cheese', 'Friggitello Peppers', 'Garlic', 'Genoa Salami', 'Goat Cheese', 'Gorgonzola Piccante Cheese', 'Gouda Cheese', 'Green Olives', 'Green Peppers', 'Italian Sausage', 'Jalapeno Peppers', 'Kalamata Olives', 'Luganega Sausage', 'Mozzarella Cheese', 'Mushrooms', 'Onions', 'Oregano', 'Pancetta', 'Parmigiano Reggiano Cheese', 'Pears', 'Peperoncini verdi', 'Pepperoni', 'Pesto Sauce', 'Pineapple', 'Plum Tomatoes', 'Prosciutto', 'Prosciutto di San Daniele', 'Provolone Cheese', 'Red Onions', 'Red Peppers', 'Ricotta Cheese', 'Romano Cheese', 'Sliced Ham', 'Smoked Gouda Cheese', 'Soppressata Salami', 'Spinach', 'Sun-dried Tomatoes', 'Thai Sweet Chilli Sauce', 'Thyme', 'Tomatoes', 'Zucchini'). 
    Return "Not mentioned" if a value is not mentioned.

    Query: "{query}"

    Please ensure that the values are unique and clear. If a value is not provided, 
    return "Not mentioned" for that entity.
    """

    response = client.responses.create(
        model="gpt-4", 
        input=prompt,  
    )

    response_text = response.output[0].content[0].text
    print(response_text)
    size = "Not mentioned"
    money = "Not mentioned"
    category = "Not mentioned"
    ingredients = "Not mentioned"
    
    if "Size:" in response_text:
        size = response_text.split("Size:")[1].split("\n")[0].strip()
    if "Money:" in response_text:
        money = response_text.split("Money:")[1].split("\n")[0].strip()
    if "Category:" in response_text:
        category = response_text.split("Category:")[1].split("\n")[0].strip()
    if "Ingredients:" in response_text:
        ingredients = response_text.split("Ingredients:")[1].split("\n")[0].strip()

    size = size if size != "Not mentioned" else None
    money = money if money != "Not mentioned" else None
    category = category if category != "Not mentioned" else None
    ingredients = ingredients if ingredients != "Not mentioned" else None

    return size, money, category, ingredients

@router.post("/search_NLP")
async def search_pizza(request: QueryRequest):
    size, money, category, ingredients = extract_entities_from_query(request.query)

    target_price = None
    if money == "low":
        target_price = 10 
    elif money == "medium":
        target_price = 17  
    elif money == "high":
        target_price = 28  

    pizzas = get_pizza_data(size=size, money=money, category=category, ingredients=ingredients, target_price=target_price)

    if not pizzas:
        raise HTTPException(status_code=404, detail="No pizzas match the search criteria")

    pizza_names = list({pizza.pizza_name for pizza in pizzas})


    return {"suggested_pizzas": pizza_names}
