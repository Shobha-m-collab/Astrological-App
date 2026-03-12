import ollama
import re

def generate_response(message, zodiac, history, context, language="en"):
    
    # 1. Format context and history cleanly
    context_text = "\n".join([f"- {doc['text']}" for doc in context]) if context else "None."
    
    # 2. Handle the Empty History Edge Case
    if history:
        history_text = "\n".join([f"User: {h['user']}\nYou: {h['assistant']}" for h in history])
    else:
        history_text = "EMPTY. This is the very first message of the conversation."

    lang_instruction = "Respond strictly in Hindi." if language == "hi" else "Respond in English."

    # 3. Strengthened System Prompt Guardrails
    system_prompt = f"""You are Astro, an expert, concise astrology assistant.
User Zodiac: {zodiac}.
{lang_instruction}

CRITICAL RULES:
1. Respond under 5 sentences.
2. You are the assistant. NEVER generate follow-up questions, user prompts, or instructions.
3. If the user asks for a summary, but the Conversation History is "EMPTY", politely explain that there is no past conversation to summarize yet, and offer to give them general astrology guidance for their Zodiac sign.
4. Base your answers on the provided Astrological Facts if available. 
5.Try to give positive answers when 'retrieval_used' is false.
"""

    user_prompt = f"""Conversation History:
{history_text}

Astrological Facts:
{context_text}

User Question: {message}

Assistant Response:"""

    # 4. Call Ollama
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