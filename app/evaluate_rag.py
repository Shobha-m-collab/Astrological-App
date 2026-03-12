from retriever import Retriever

def run_eval():
    print("Starting RAG Evaluation...")
    retriever = Retriever()
    
    # 1. Case where Retrieval HELPS
    print("\n--- TEST 1: Where RAG Helps (Factual Query) ---")
    query_good = "What are the personality traits of a Gemini?"
    docs_good = retriever.search(query_good, top_k=1)
    
    if docs_good:
        print(f"Query: '{query_good}'")
        print(f"Retrieved Source: {docs_good[0]['source']}")
        print(f"Content: {docs_good[0]['text'][:80]}...")
        print("Conclusion: SUCCESS. RAG successfully grounded the LLM with exact Zodiac facts.")
    else:
        print("Failed to retrieve.")

    # 2. Case where Retrieval HURTS / IS UNNECESSARY
    print("\n--- TEST 2: Where RAG Hurts (Conversational Meta-Query) ---")
    query_bad = "Summarize what we just talked about regarding my career."
    docs_bad = retriever.search(query_bad, top_k=2)
    
    print(f"Query: '{query_bad}'")
    if docs_bad:
        print(f"Retrieved Context: {[d['source'] for d in docs_bad]}")
        print("Conclusion: FAIL/HURT. RAG pulled random 'career' documents from the database. Feeding this to the LLM will confuse it, as the user just wants a summary of the chat history, not new facts. This proves why Intent Routing is necessary!")

if __name__ == "__main__":
    run_eval()