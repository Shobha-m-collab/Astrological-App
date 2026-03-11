from app.llm import generate_response
from app.chat_service import chat


'''response = generate_response(
    message="How will my career be this month?",
    zodiac="Leo",
    context=["Leo thrives in leadership roles and creative work."]
)'''

#print(response)

#Test chat_service

request = {
    "session_id": "abc123",
    "message": "How will my career be this month?",
    "user_profile": {
        "name": "Ritika",
        "birth_date": "1995-08-20",
        "birth_time": "14:30",
        "birth_place": "Jaipur, India",
        "preferred_language": "en"
    }
}

response_chat = chat(request)

print(response_chat)