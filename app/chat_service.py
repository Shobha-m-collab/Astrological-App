from .zodiac import get_zodiac
from .llm import ensure_model_exists,generate_response

ensure_model_exists("phi3:mini")

def chat(payload: dict, retriever, memory, router):
    session_id = payload.get("session_id")
    message = payload.get("message")
    user_profile = payload.get("user_profile", {})

    birth_date = user_profile.get("birth_date")
    preferred_language = user_profile.get("preferred_language", "en")

    # Fast computations (~1ms)
    zodiac = get_zodiac(birth_date)
    history = memory.get_history(session_id)
    retrieval_used = router.should_retrieve(message)

    # Retrieval (~50ms, index is already in RAM)
    retrieved_docs = []
    context_used = []

    if retrieval_used:
        # Appending Zodiac naturally guides the vector search
        expanded_query = f"{message} {zodiac}"
        retrieved_docs = retriever.search(expanded_query, top_k=2)
        context_used = list(set([doc["source"] for doc in retrieved_docs]))

    # LLM Generation (~800ms to 1.5s depending on Ollama speed)
    response = generate_response(
        message=message,
        zodiac=zodiac,
        history=history,
        context=retrieved_docs,
        language=preferred_language
    )

    # Save to memory (~1ms)
    memory.save_turn(session_id, message, response)

    return {
        "response": response,
        "zodiac": zodiac,
        "context_used": context_used,
        "retrieval_used": retrieval_used
    }