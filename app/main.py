from fastapi import FastAPI
from starlette.middleware.cors import CORSMiddleware
from app.routers.home import router as home_router
from app.routers.recommender import router as recommender
from app.routers.addknow import router as addknow
from app.routers.chatbot import router as chatbot
app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"]
)

app.include_router(home_router)
app.include_router(recommender)
app.include_router(addknow)
app.include_router(chatbot)