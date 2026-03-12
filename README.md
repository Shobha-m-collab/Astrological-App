# 🌌 Astrology AI Assistant 

An intelligent, multi-turn conversational AI model that provides personalized astrological guidance using **Retrieval-Augmented Generation (RAG)** and **Intent-Aware Routing**. 

Built for high-performance and low latency, this API leverages a local LLM to answer contextual astrology questions while strictly managing conversation state and context windows.

## 🎯 Core Features (Assignment Rubric)
- **State Ownership & Memory:** Implements a sliding-window memory system (Last-N turns) tied to a unique `session_id` for controlled context growth.
- **Intent-Aware RAG:** Features an O(1) keyword-based intent router that explicitly decides *when* to search the vector database and *when* to rely purely on conversational memory, preventing hallucination and saving compute.
- **Hybrid Retrieval:** Combines semantic search (FAISS + SentenceTransformers) with keyword matching (BM25) and distance thresholds to ensure only highly relevant context is retrieved.
- **Dynamic Personalization:** Deterministically calculates the user's Zodiac (Sun Sign) based on their Date of Birth and grounds the LLM prompt in their specific astrological traits.
- **Bilingual Support:** Supports a seamless toggle between English and Hindi ('preferred_language: "hi"').

---

## 🏗️ System Architecture
1. **API Layer (FastAPI):** Exposes a '/chat' POST endpoint. Uses the 'lifespan' context manager to load ML models and Vector DBs into RAM *exactly once* on startup, reducing request latency from seconds to milliseconds.
2. **Intent Router Layer:** Parses the user's message. Meta-queries ("summarize", "repeat") bypass the retrieval layer entirely.
3. **Retrieval Layer:** If astrological facts are needed, queries the hybrid FAISS/BM25 vector store. Text is chunked securely (handling nested JSONs and paragraph-separated TXTs).
4. **Memory Layer:** Fetches the Last-N turns for the given 'session_id'.
5. **LLM Layer:** Constructs a strict, instruction-bound prompt and generates the response using a local Ollama daemon.

---

## 🧠 Engineering Decisions & Trade-offs

To meet the "Quality & Cost Awareness" requirement, the following architectural trade-offs were made:

### 1. Model Selection: 'phi3:mini 'vs 'llama3:8b'
- **Decision:** I chose Microsoft's 'phi3:mini' (3.8B parameters) as the default local model over Llama 3 (8B). 
- **Trade-off:** While Llama 3 generates slightly more natural Devanagari script for the Hindi toggle, it takes ~5+ seconds per inference on a standard CPU. 'phi3:mini' allows the entire pipeline to execute end-to-end in **~1-2 seconds**, prioritizing the UX requirement of low-latency conversational AI over marginal linguistic perfection.

### 2. Intent Routing: Deterministic vs. LLM-based
- **Decision:** The Intent Router uses a hashed keyword/regex approach rather than a secondary "Classifier LLM".
- **Trade-off:** Using an LLM to classify user intent (e.g., "Does this need RAG?") is highly accurate but introduces a "Double LLM Call," doubling latency and token costs. A deterministic router is O(1) and instantaneous, easily handling 95% of standard routing cases at zero cost.

### 3. Latency Optimization via App State Injection
- **Decision:** The Embedding Model ('all-MiniLM-L6-v2') and FAISS index are initialized inside FastAPI's '@asynccontextmanager lifespan'. 
- **Trade-off:** This increases server startup time by ~3 seconds and holds a persistent memory footprint in RAM. However, it entirely eliminates disk I/O and model-loading overhead during API calls, dropping backend processing time to **< 50ms**.

### 4. Controlled Output formatting
- **Decision:** Added a regex-based post-processing step to the LLM output.
- **Trade-off:** Small open-source models occasionally hallucinate structural tokens (e.g., '\n\nSummary:').
- Regex cleanup ensures the API contract is strictly honored and the frontend receives a clean JSON payload, adding robust defensive programming to the pipeline.

### 5. Addressing Model Confusion
- **The Issue:** When context is sparse (e.g., empty history), the model's text-completion core can trigger "Prompt Bleed," where it begins generating self-directed instructions or meta-commentary on the prompt itself.
- **The Resolution:** Implemented ML-engineering guardrails to handle null history states and added response truncation layers to prevent recursive instruction generation.
---

## 🚀 Setup & Installation

### Prerequisites
- Python 3.10+
- - 'uv' package manager (or pip).
- [Ollama](https://ollama.com/) installed, pulled and run locally.


**1. Pull the Local LLM if it doesn't get pulled automatically**
Ensure your local Ollama daemon is running:

**2. Execute main.py using uv or pip** [ cmd: uv run main.py]
  
After 2-3 sec you should see some messages like this:
  
<img width="586" height="138" alt="image" src="https://github.com/user-attachments/assets/afde755f-0809-4a44-9b9a-b399071ffc8f" />

Please visit **http://127.0.0.1:8000/docs** to chat with the agent! 

Thank you! 

