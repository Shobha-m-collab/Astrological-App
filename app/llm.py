import ollama


def generate_response(message, zodiac, history, context, language="en"):

    # -----------------------------------
    # Convert retrieved docs to text
    # -----------------------------------
    context_text = ""

    if context:
        context_text = "\n".join([doc["text"] for doc in context])

    # -----------------------------------
    # Format conversation history
    # -----------------------------------
    history_text = ""

    if history:
        history_text = "\n".join(history)

    # -----------------------------------
    # Language instruction
    # -----------------------------------
    if language == "hi":
        language_instruction = "Respond in Hindi."
    else:
        language_instruction = "Respond in English."

    # -----------------------------------
    # System Prompt (controls behavior)
    # -----------------------------------
    system_prompt = f"""
You are an astrology assistant.

Guidelines:
- Provide the answer as plain text.
- Do not use bullet points, markdown, or special formatting.
- Use the provided astrology knowledge when relevant.
- Do not invent planetary positions or birth chart details.
- Keep the response concise (80–120 words).
- Give helpful astrology-based guidance, not deterministic predictions.
- If no relevant context is provided, answer generally using astrology knowledge.

User Zodiac Sign: {zodiac}

{language_instruction}
"""

    # -----------------------------------
    # Final user prompt
    # -----------------------------------
    user_prompt = f"""
Conversation History:
{history_text}

Astrology Knowledge:
{context_text}

User Question:
{message}
"""

    # -----------------------------------
    # Call Ollama
    # -----------------------------------
    response = ollama.chat(
        model="llama3",
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ]
    )

    return response["message"]["content"]