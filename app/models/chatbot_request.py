from pydantic import BaseModel
class ChatbotRequest(BaseModel):
    # title: str  
    idPost: str
    question: str  
