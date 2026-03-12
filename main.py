import uvicorn
from contextlib import asynccontextmanager
from fastapi import FastAPI, Request
from pydantic import BaseModel, Field

# Import your components based on your directory structure
from app.chat_service import chat
from app.retriever import Retriever        
from app.memory import MemoryManager       
from app.intent_router import IntentRouter 

# Lifespan (loads Heavy ML Models once)
@asynccontextmanager
async def lifespan(app: FastAPI):
    print("🚀 Starting up: Loading Vector DB, Memory, and Models into RAM...")
    
    # Initialize heavy resources ONCE and store them in app.state
    app.state.retriever = Retriever()  
    app.state.memory = MemoryManager() 
    app.state.router = IntentRouter()  
    
    print("✅ All resources loaded successfully! API is ready.")
    yield
    print("🛑 Shutting down: Cleaning up resources...")


# INITIALIZE 'app'
app = FastAPI(
    title="Astrology RAG Assistant",
    description="Astrology chatbot with retrieval-augmented generation",
    version="1.0",
    lifespan=lifespan
)


# Pydantic Models for Swagger UI Documentation
class UserProfile(BaseModel):
    name: str = Field(..., description="User's full name", examples=["Ritika"])
    birth_date: str = Field(..., description="Birth date strictly in YYYY-MM-DD format", examples=["1995-08-20"])
    birth_time: str = Field(..., description="Birth time in HH:MM format (24-hour)", examples=["14:30"])
    birth_place: str = Field(..., description="City and Country of birth", examples=["Jaipur, India"])
    preferred_language: str = Field(default="en", description="Language code ('en' or 'hi')", examples=["hi"])

class ChatRequest(BaseModel):
    session_id: str = Field(..., description="Unique session ID for memory", examples=["abc-123"])
    message: str = Field(..., description="User message", examples=["How will my month be in career?"])
    user_profile: UserProfile

    model_config = {
        "json_schema_extra": {
            "example": {
                "session_id": "session-123",
                "message": "How will my month be in career?",
                "user_profile": {
                    "name": "Priyanka",
                    "birth_date": "1995-08-20",
                    "birth_time": "14:30",
                    "birth_place": "Bangalore, India",
                    "preferred_language": "en",
                   # "goals": "career growth"
                }
            }
        }
    }


# Endpoints
@app.post("/chat")
async def chat_endpoint(request: ChatRequest, fastapi_req: Request):
    # Fetch pre-loaded instances from app state
    retriever = fastapi_req.app.state.retriever
    memory = fastapi_req.app.state.memory
    router = fastapi_req.app.state.router

    # Convert Pydantic model to dictionary 
    payload = request.model_dump()

    # Pass the payload AND the pre-loaded instances to your chat service
    response = chat(
        payload=payload,
        retriever=retriever,
        memory=memory,
        router=router
    )

    return response


# Start the server (Required when using `uv run main.py` or `python main.py`)
if __name__ == "__main__":
    # This runs uvicorn programmatically
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)