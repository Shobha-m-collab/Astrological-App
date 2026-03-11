from zodiac import get_zodiac
from memory import get_history, save_turn
from intent_router import should_retrieve
from retriever import Retriever



#test zodiac.py
#print(get_zodiac("1995-08-20"))

#test memory

session_id = "test123"

save_turn(session_id, "Hello", "Hi there")
save_turn(session_id, "How are you?", "I'm good")

history = get_history(session_id)

print("memory test result: " )
print(history)

#test intent_router
print ("test result of intent_router:")
print(should_retrieve("How will my career be this month?"))  # True
print(should_retrieve("Which planet affects love?"))         # True
print(should_retrieve("Summarize what you told me"))         # False
print(should_retrieve("Why are you repeating yourself?"))    # False

#test retriever
r = Retriever()

result = r.search("Which planet affects love?")
print("retriever performance:")
print("Retrieved docs:")
print(result["documents"])

print("\nContext used:")
print(result["context_used"])

#test llm
from llm import generate_response

response = generate_response(
    message="How will my career be?",
    zodiac="Leo",
    history=[],
    context=["Opportunities may arise in leadership roles today."],
    language="en"
)

print(response)