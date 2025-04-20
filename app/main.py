from fastapi import FastAPI
from starlette.middleware.cors import CORSMiddleware
from app.routers.home import router as home_router
from app.routers.recommender import router as recommender
from app.routers.addknow import router as addknow
from app.routers.chatbot import router as chatbot
from app.routers.search_NLP import router as search_NLP
from app.routers.show_Olap import router as show_Olap
from app.routers.dashboard import router as dashboard
from app.routers.post_router import router as post
from app.routers.search_router import router as search
from app.routers.sentiment_router import router as sentiment
from app.routers.chatbot_inpost import router as chatbott
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
app.include_router(search_NLP)
app.include_router(show_Olap)
app.include_router(dashboard)
app.include_router(post)
app.include_router(search)
app.include_router(sentiment)
app.include_router(chatbott)