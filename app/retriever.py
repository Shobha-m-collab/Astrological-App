import os
import json
import faiss
import numpy as np
from sentence_transformers import SentenceTransformer
from rank_bm25 import BM25Okapi

DATA_PATH = "data"

class Retriever:

    def __init__(self):

        self.model = SentenceTransformer("all-MiniLM-L6-v2")

        self.docs = []
        self.sources = []

        texts = []

        # load JSON files
        for file in os.listdir(DATA_PATH):

            if file.endswith(".json"):

                path = os.path.join(DATA_PATH, file)

                with open(path, "r", encoding="utf-8") as f:

                    data = json.load(f)

                    for item in data:

                        if isinstance(item, dict):
                            text = item.get("text", "")

                        elif isinstance(item, str):
                            text = item
                        else:
                            continue
                        
                        texts.append(text)

                        self.docs.append({
                            "text": text,
                            "source": file.replace(".json","")
                        })

        # embeddings
        embeddings = self.model.encode(texts)

        dim = embeddings.shape[1]

        self.index = faiss.IndexFlatL2(dim)

        self.index.add(np.array(embeddings))

        # build BM25
        tokenized = [doc["text"].lower().split() for doc in self.docs]
        self.bm25 = BM25Okapi(tokenized)

        print("Retriever initialized with", len(self.docs), "documents")

    def search(self, query, top_k=3):

        # -----------------
        # FAISS SEARCH
        # -----------------

        query_embedding = self.model.encode([query])

        D, I = self.index.search(np.array(query_embedding), top_k)

        faiss_docs = [self.docs[i] for i in I[0]]

        # -----------------
        # BM25 SEARCH
        # -----------------

        tokenized_query = query.lower().split()

        bm25_scores = self.bm25.get_scores(tokenized_query)

        bm25_indices = np.argsort(bm25_scores)[::-1][:top_k]

        bm25_docs = [self.docs[i] for i in bm25_indices]

        # -----------------
        # COMBINE RESULTS
        # -----------------

        combined = {}

        for d in faiss_docs + bm25_docs:

            combined[d["text"]] = d

        results = list(combined.values())[:top_k]

        print("Retrieved sources:", [r["source"] for r in results])

        return results