from fastapi import APIRouter, HTTPException
from app.models.post_request import PostRequest
from app.services.qdrant_service import add_post_to_qdrant, store_data_in_qdrant, create_new_collection, insert_embeddings
from fastapi import APIRouter, HTTPException
from sentence_transformers import SentenceTransformer
from app.services.qdrant_service import create_new_collection
import requests
from app.core.clean_text import clean_text

model_name = "hothanhtienqb/mind_map_blog_model"
model = SentenceTransformer(model_name)
router = APIRouter()
# from app.models.store_request import StoreRequest


@router.post("/add_post")
async def add_post(request: PostRequest):
    try:
        add_post_to_qdrant(request.collection_name , request.title, request.content)
        return {
             "message": f"Thêm post vào collection {request.collection_name} thành công"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    
@router.post("/add_posts_inapi")
async def add_posts_inapi(collection_name: str, api_url: str, token: str):
    """
    Thêm các bài viết từ API bên ngoài vào Qdrant sau khi tiền xử lý.
    
    Args:
        collection_name (str): Tên collection trong Qdrant.
        api_url (str): URL của API cung cấp dữ liệu bài viết.
        token (str): Token authorization để truy cập API.

    Returns:
        dict: Kết quả thành công hoặc thông báo lỗi.
    """
    try:
        headers = {
            "Authorization": f"{token}"
        }
        response = requests.get(api_url, headers=headers)
        response.raise_for_status()
        data = response.json()
        posts = data.get("data", [])
        create_new_collection('post')
        if not isinstance(posts, list):
            raise HTTPException(status_code=400, detail="Dữ liệu API không hợp lệ.")

        titles = [clean_text(post["title"]) for post in posts]
        contents = [clean_text(post["body"]) for post in posts]

        embeddings = model.encode(contents)
        
        payloads = [{"id": post["id"], "title": title, "content": content} for post, title, content in zip(posts, titles, contents)]

        insert_embeddings(collection_name, embeddings, payloads) 

        return {"message": f"Đã thêm {len(posts)} bài viết vào collection '{collection_name}' thành công."}

    except requests.exceptions.RequestException as e:
        raise HTTPException(status_code=500, detail=f"Lỗi khi gọi API: {str(e)}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Lỗi khi thêm bài viết vào Qdrant: {str(e)}")