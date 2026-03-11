from fastapi import FastAPI
from pydantic import BaseModel
from app.chat_service import chat

app = FastAPI(
    title="Astrology RAG Assistant",
    description="Astrology chatbot with retrieval-augmented generation",
    version="1.0"
)


class UserProfile(BaseModel):
    name: str
    birth_date: str
    birth_time: str
    birth_place: str
    preferred_language: str = "en"


class ChatRequest(BaseModel):
    session_id: str
    message: str
    user_profile: UserProfile


@app.post("/chat")
def chat_endpoint(request: ChatRequest):

    response = chat(request.dict())

    return response