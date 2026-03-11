from .memory import get_history, save_turn
from .zodiac import get_zodiac
from .intent_router import should_retrieve
from .retriever import Retriever
from .llm import generate_response


# initialize retriever once (avoids rebuilding index every request)
retriever = Retriever()


def chat(request):

    session_id = request.get("session_id")
    message = request.get("message")
    user_profile = request.get("user_profile", {})

    # -----------------------------
    # Extract user profile fields
    # -----------------------------
    birth_date = user_profile.get("birth_date")
    preferred_language = user_profile.get("preferred_language", "en")

    # -----------------------------
    # Determine zodiac
    # -----------------------------
    zodiac = get_zodiac(birth_date)

    # -----------------------------
    # Retrieve conversation history
    # -----------------------------
    history = get_history(session_id)

    # -----------------------------
    # Decide if retrieval is needed
    # -----------------------------
    retrieval_used = should_retrieve(message)

    retrieved_docs = []
    context_used = []

    # -----------------------------
    # Hybrid Retrieval
    # -----------------------------
    if retrieval_used:

        # Query expansion improves recall
        expanded_query = f"{message} astrology zodiac horoscope prediction relationships career"

        docs = retriever.search(expanded_query)

        retrieved_docs = docs

        # extract sources used
        context_used = list(set([doc["source"] for doc in docs]))

    # -----------------------------
    # Generate LLM response
    # -----------------------------
    response = generate_response(
        message=message,
        zodiac=zodiac,
        history=history,
        context=retrieved_docs,
        language=preferred_language
    )

    # -----------------------------
    # Save conversation turn
    # -----------------------------
    save_turn(session_id, message, response)

    # -----------------------------
    # API response format
    # -----------------------------
    return {
        "response": response,
        "zodiac": zodiac,
        "context_used": context_used,
        "retrieval_used": retrieval_used
    }