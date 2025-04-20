from pydantic import BaseModel

class SentimentRequest(BaseModel):
    sentence: str
