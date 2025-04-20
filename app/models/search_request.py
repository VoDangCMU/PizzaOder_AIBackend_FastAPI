from pydantic import BaseModel

class SearchRequest(BaseModel):
    content: str
    limit: int
