import os
import json
import faiss
import numpy as np
from sentence_transformers import SentenceTransformer
from rank_bm25 import BM25Okapi

DATA_PATH = "data"

class Retriever:
    def __init__(self):
        print("⏳ Loading Embedding Model into RAM (This happens only once)...")
        # all-MiniLM-L6-v2 is ultra-fast, perfect for 1-sec latency targets
        self.model = SentenceTransformer("all-MiniLM-L6-v2")
        self.docs = []
        
        self._load_and_chunk_data()

        if not self.docs:
            print("⚠️ Warning: No documents found in data/ folder!")
            return

        texts = [doc["text"] for doc in self.docs]
        
        # Build FAISS
        embeddings = self.model.encode(texts)
        dim = embeddings.shape[1]
        self.index = faiss.IndexFlatL2(dim)
        self.index.add(np.array(embeddings))

        # Build BM25
        tokenized = [text.lower().split() for text in texts]
        self.bm25 = BM25Okapi(tokenized)

        print(f"✅ Retriever initialized with {len(self.docs)} chunks")

    def _load_and_chunk_data(self):
        """Smart chunking for both .txt and .json files"""
        if not os.path.exists(DATA_PATH):
            os.makedirs(DATA_PATH)
            
        for file in os.listdir(DATA_PATH):
            path = os.path.join(DATA_PATH, file)
            source_name = file.replace(".json", "").replace(".txt", "")

            # 1. Chunking Text Files (Split by Paragraphs)
            if file.endswith(".txt"):
                with open(path, "r", encoding="utf-8") as f:
                    content = f.read()
                    # Chunk by double newline (paragraphs)
                    paragraphs = [p.strip() for p in content.split("\n\n") if p.strip()]
                    for p in paragraphs:
                        self.docs.append({"text": p, "source": source_name})

            # 2. Chunking JSON Files (Handling Nested Dictionaries)
            elif file.endswith(".json"):
                with open(path, "r", encoding="utf-8") as f:
                    try:
                        data = json.load(f)
                        # Handle Dict formatting (e.g., zodiac_traits.json or planetary_impacts.json)
                        if isinstance(data, dict):
                            for key, val in data.items():
                                if isinstance(val, dict):
                                    # Flatten nested dicts: "Aries: personality is Bold. strengths are..."
                                    flattened = " ".join([f"{k} is {v}" for k, v in val.items()])
                                    text = f"{key}: {flattened}"
                                else:
                                    text = f"{key}: {val}"
                                self.docs.append({"text": text, "source": source_name})
                    except json.JSONDecodeError:
                        continue

    def search(self, query, top_k=2, distance_threshold=1.5):
        """Hybrid Search with Thresholding to discard irrelevant context."""
        if not self.docs: return []

        # FAISS SEARCH
        query_embedding = self.model.encode([query])
        D, I = self.index.search(np.array(query_embedding), top_k)
        
        faiss_docs = []
        for dist, idx in zip(D[0], I[0]):
            if dist < distance_threshold:  # Lower distance is better in L2
                faiss_docs.append(self.docs[idx])

        # BM25 SEARCH
        tokenized_query = query.lower().split()
        bm25_scores = self.bm25.get_scores(tokenized_query)
        bm25_indices = np.argsort(bm25_scores)[::-1][:top_k]
        
        # Only keep BM25 if score > 0
        bm25_docs = [self.docs[i] for i in bm25_indices if bm25_scores[i] > 0]

        # COMBINE & DEDUPLICATE
        combined = {d["text"]: d for d in faiss_docs + bm25_docs}
        results = list(combined.values())[:top_k]

        return results