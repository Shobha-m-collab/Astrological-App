import ollama
import re

def ensure_model_exists(model_name="phi3:mini"):
    try:
        # Check if model exists locally
        ollama.show(model_name)
    except ollama.ResponseError:
        print(f"Model {model_name} not found. Pulling now...")
        ollama.pull(model_name)


def generate_response(message, zodiac, history, context, language="en"):
    
    # Format context and history cleanly
    context_text = "\n".join([f"- {doc['text']}" for doc in context]) if context else "None."
    
    # Handle the Empty History Edge Case
    if history:
        history_text = "\n".join([f"User: {h['user']}\nYou: {h['assistant']}" for h in history])
    else:
        history_text = "EMPTY. This is the very first message of the conversation."

    lang_instruction = "Respond strictly in Hindi." if language == "hi" else "Respond in English."

    # Strengthened System Prompt Guardrails
    system_prompt = f"""You are Astro, an expert, concise astrology assistant.
User Zodiac: {zodiac}.
{lang_instruction}

CRITICAL RULES:
- Respond in 5 sentences.
- Use the provided context if available.
- If context is provided, base your answer heavily on it.
- If the user asks for a summary, but the Conversation History is "EMPTY", politely explain that there is no past conversation to summarize yet, and offer to give them general astrology guidance for their Zodiac sign.
- Do NOT use markdown (no asterisks, bolding, or lists).
- Do NOT use line breaks, newlines, or bullet points.
- Do NOT include headers like "Summary:" or "Conclusion:".
- If context is missing, give general, positive astrological guidance.
- You are the assistant. NEVER generate user prompts, or instructions.
"""

    user_prompt = f"""Conversation History:
{history_text}

Astrological Facts:
{context_text}

User Question: {message}

Assistant Response:"""

    # Call Ollama
    response = ollama.chat(
        model="phi3:mini", # or llama3:8b
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ]
    )

    raw_content = response["message"]["content"]

    # --- AGGRESSIVE CLEANUP LOGIC ---
    
    # If the model hallucinates and adds "\n\nSummarize this...", we cut off 
    # everything after the first double-newline to keep only the actual answer.
    if "\n\n" in raw_content:
        raw_content = raw_content.split("\n\n")[0]

    # Clean up any remaining rogue newlines or extra spaces
    clean_content = re.sub(r'\s+', ' ', raw_content).strip()

    # Remove hallucinated prefixes/suffixes if they appear
    bad_phrases = ["Summary:", "Conclusion:", "Assistant Response:"]
    for phrase in bad_phrases:
        clean_content = clean_content.replace(phrase, "").strip()

    return clean_content