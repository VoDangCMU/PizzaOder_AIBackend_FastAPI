from fastapi import APIRouter, HTTPException
from langchain.schema import Document
from langchain_openai import OpenAIEmbeddings 
from qdrant_client import QdrantClient
from qdrant_client.models import PointStruct
from qdrant_client.http import models as qmodels  
import os
from dotenv import load_dotenv
import uuid

load_dotenv()

apikey = os.getenv("api_key")

embeddings = OpenAIEmbeddings(openai_api_key=apikey) 
qdrant_client = QdrantClient(host="localhost", port=6333)  

router = APIRouter()

documents = [
    Document(page_content="Võ Đang Pizza Shop được sáng lập bởi Hồ Thành Tiến, Nguyễn Bá Khoa, Hồ Tấn Phong, Trần Đình Quân, Trần Nguyễn Quốc Bảo.",
              metadata={"tag": "Võ Đang Pizza", "founders": "Hồ Thành Tiến, Nguyễn Bá Khoa, Hồ Tấn Phong, Trần Đình Quân, Trần Nguyễn Quốc Bảo"}),
    Document(page_content="Võ Đang Pizza có chi nhánh tại 554 Điện Biên Phủ, Đà Nẵng. Hotline: 0912590577. Email: hothanhtienqb@gmail.com.",
              metadata={"tag": "Võ Đang Pizza", "address": "554 Điện Biên Phủ, Đà Nẵng", "hotline": "0912590577", "email": "hothanhtienqb@gmail.com"}),
    
    Document(page_content="The Hawaiian Pizza - Size: M, Category: Classic, Ingredients: Sliced Ham, Pineapple, Mozzarella Cheese",
              metadata={"pizza_tag": "The Hawaiian Pizza", "size_tag": "M", "category_tag": "Classic", "ingredients_tag": "Sliced Ham, Pineapple, Mozzarella Cheese"}),
    Document(page_content="The Classic Deluxe Pizza - Size: M, Category: Classic, Ingredients: Pepperoni, Mushrooms, Red Onions, Red Peppers, Mozzarella Cheese",
              metadata={"pizza_tag": "The Classic Deluxe Pizza", "size_tag": "M", "category_tag": "Classic", "ingredients_tag": "Pepperoni, Mushrooms, Red Onions, Red Peppers, Mozzarella Cheese"}),
    Document(page_content="The Five Cheese Pizza - Size: L, Category: Veggie, Ingredients: Mozzarella Cheese, Provolone Cheese, Smoked Gouda, Parmesan, Feta Cheese",
              metadata={"pizza_tag": "The Five Cheese Pizza", "size_tag": "L", "category_tag": "Veggie", "ingredients_tag": "Mozzarella Cheese, Provolone Cheese, Smoked Gouda, Parmesan, Feta Cheese"}),
    
    Document(page_content="Pizza tại Võ Đang Pizza được chia thành các thể loại như Classic, Veggie, Supreme.",
              metadata={"tag": "Pizza Categories", "categories": "Classic, Veggie, Supreme"}),
    Document(page_content="Các kích thước pizza tại Võ Đang Pizza gồm có M (Medium), L (Large).",
              metadata={"tag": "Pizza Sizes", "sizes": "M, L"}),
]

def create_collection():
    try:
        qdrant_client.create_collection(
            collection_name="pizza_shop_knowledge",
            vectors_config=qmodels.VectorParams(size=1536, distance="Cosine") 
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail="Error creating collection: " + str(e))


@router.post("/add_knowledge")
async def add_knowledge():
    try:
        create_collection()
        for document in documents:
            vector = embeddings.embed_documents([document.page_content])[0]  
            
            point_id = str(uuid.uuid4())  
            
            point = PointStruct(
                id=point_id, 
                vector=vector, 
                payload={**document.metadata, "page_content": document.page_content} 
            )
            
            qdrant_client.upsert(
                collection_name="pizza_shop_knowledge",
                points=[point]
            )
        
        return {"message": "Knowledge added successfully!"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
