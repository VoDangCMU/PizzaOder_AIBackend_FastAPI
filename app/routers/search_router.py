from fastapi import APIRouter, HTTPException
from app.models.search_request import SearchRequest
from app.services.qdrant_service import search_in_qdrant

router = APIRouter()

@router.post("/search")
async def search(request: SearchRequest):
    try:
        collection_name = "post"
        results = search_in_qdrant(collection_name, request.content, request.limit)
        return {
            "results": [
                {
                    "id": result.payload['id'],
                    "title": result.payload['title'], 
                    "similarity": result.score,
                    "content": result.payload['content']
                } 
                for result in results
            ]
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
