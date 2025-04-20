# app/routers/sentiment.py
from fastapi import APIRouter, HTTPException
from app.models.sentiment_request import SentimentRequest
from app.services.sentiment_service import predict_emotion
import requests
router = APIRouter()

@router.post("/predict_emotion")
async def predict_emotion_route(request: SentimentRequest):
    try:
        data = {
            "id": "10",
            "token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VySUQiOiIxIiwic2Vzc2lvbklEIjoiOTg4NzExZTYtNzJlZi00MGYwLTk4NmQtODA0OWVkMDJjZWMwIiwiaWF0IjoxNzMzNjQ4OTgyLCJleHAiOjE3MzQyNTM3ODJ9.6Aw3zklu4G_iaX8ID3TZQwzKSuMfQtjAojmmAzZFLvk"
        }

        # headers = {
        #     "Content-Type": "application/json"
        # }

        print('1')
        # response = requests.post("http://localhost:8000/processPost", json=data)
        # --
        predicted_emotion = predict_emotion(request.sentence)
        return {"sentence": request.sentence, "predicted_emotion": predicted_emotion}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
