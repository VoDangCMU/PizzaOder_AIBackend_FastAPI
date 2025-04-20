from fastapi import APIRouter, HTTPException
from langchain_openai import OpenAIEmbeddings
from qdrant_client import QdrantClient
from openai import OpenAI
import uuid
from pydantic import BaseModel  
import os
from dotenv import load_dotenv

load_dotenv()

router = APIRouter()

apikey = os.getenv("api_key")

embeddings = OpenAIEmbeddings(openai_api_key=apikey) 
qdrant_client = QdrantClient(host="localhost", port=6333) 
client = OpenAI(api_key=apikey)

class QueryRequest(BaseModel):
    query: str  


@router.post("/chat")
async def chat(request: QueryRequest):
    try:
        query = request.query 
        query_vector = embeddings.embed_documents([query])[0]
        
        search_results = qdrant_client.search(
            collection_name="pizza_shop_knowledge",
            query_vector=query_vector,
            limit=3
        )

        context = ""
        for result in search_results:
            context += f"Context: {result.payload['page_content']}\n"
        
        prompt = f"Here is some information: {context}\nAnswer the following question: {query}"

        print(f"Sending prompt to OpenAI: {prompt}")  
        response = client.responses.create(
            model="gpt-4",
            input=prompt
        )

        print(f"Response from OpenAI: {response}") 

        answer = response.output[0].content[0].text
        return {"response": answer.strip()}
       
    
    except Exception as e:
        print(f"Error: {str(e)}")  
        raise HTTPException(status_code=500, detail=str(e))


class PostRequest(BaseModel):
    title: str
    description: str 
    length: int  

@router.post("/generate_post")
async def generate_post(request: PostRequest):
    try:
        title = request.title
        description = request.description  
        length = request.length  

        prompt = f"Viết một bài blog chi tiết dựa trên ngữ cảnh sau: '{title}'. Bài viết nên dài khoảng {length} từ.Bắt đầu bằng những từ sau: '{description}' tiếp tục viết phần còn lại của bài một cách trôi chảy và giống con người"

        print(f"Sending prompt to OpenAI: {prompt}") 

        response = client.responses.create(
            model="gpt-4",
            input=prompt
        )

        print(f"Response from OpenAI: {response}")  

        answer = response.output[0].content[0].text
        return {"response": answer.strip()}
    
    except Exception as e:
        print(f"Error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))