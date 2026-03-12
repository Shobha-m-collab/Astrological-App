import uvicorn
from contextlib import asynccontextmanager
from fastapi import FastAPI, Request
from pydantic import BaseModel, Field

# Import your components
from app.chat_service import chat
from app.retriever import Retriever        
from app.memory import MemoryManager       
from app.intent_router import IntentRouter 
from app.llm import ensure_model_exists

#Pull the ollama model if it's not yet done
ensure_model_exists(model_name='phi3:mini')

# --- LIFESPAN ---
@asynccontextmanager
async def lifespan(app: FastAPI):
    print("🚀 Starting up: Loading Vector DB, Memory, and Models...")
    app.state.retriever = Retriever()  
    app.state.memory = MemoryManager() 
    app.state.router = IntentRouter()  
    print("✅ All resources loaded successfully!")
    yield
    print("🛑 Shutting down...")

# --- INITIALIZE APP ---
app = FastAPI(
    title="Astrology RAG Assistant",
    description="Astrology chatbot with retrieval-augmented generation",
    version="2.1",
    lifespan=lifespan
)

# --- INPUT SCHEMAS ---
class UserProfile(BaseModel):
    name: str = Field(..., description="User's full name")
    birth_date: str = Field(..., description="YYYY-MM-DD")
    birth_time: str = Field(..., description="HH:MM (24-hour)")
    birth_place: str = Field(..., description="City, Country")
    preferred_language: str = Field(default="en", description="Language code ('en' or 'hi')")

class ChatRequest(BaseModel):
    session_id: str
    message: str
    user_profile: UserProfile

    model_config = {
        "json_schema_extra": {
            "example": {
                "session_id": "session-123",
                "message": "How will my month be in career?",
                "user_profile": {
                    "name": "Priyanka",
                    "birth_date": "1998-01-20",
                    "birth_time": "14:30",
                    "birth_place": "Jaipur, India",
                    "preferred_language": "hi"
                }
            }
        }
    }

# --- OUTPUT SCHEMA (Strictly matches the Assignment PDF) ---
class ChatResponse(BaseModel):
    response: str
    zodiac: str
    context_used: list[str]
    retrieval_used: bool


# --- ENDPOINTS ---
@app.post("/chat", response_model=ChatResponse)
async def chat_endpoint(request: ChatRequest, fastapi_req: Request):
    # Fetch pre-loaded instances
    retriever = fastapi_req.app.state.retriever
    memory = fastapi_req.app.state.memory
    router = fastapi_req.app.state.router

    # Convert to dict
    payload = request.model_dump()
    
    # Call your chat logic
    raw_response = chat(
        payload=payload,
        retriever=retriever,
        memory=memory,
        router=router
    )

    # FastAPI will automatically validate this dict against ChatResponse
    return raw_response

# --- SERVER START ---
if __name__ == "__main__":
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)