import os
import numpy as np
import logging
from typing import List, Tuple, Dict
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from chrona.schemas.memory import Memory
from chrona.config.settings import settings

class VectorStore:
    def __init__(self):
        self.memories: List[Memory] = []
        self.mode = "tf-idf"
        self.openai_key = os.environ.get("OPENAI_API_KEY") or settings.OPENAI_API_KEY
        
        # Check for local transformer support
        self.local_model = None
        try:
            from sentence_transformers import SentenceTransformer
            self.local_model = SentenceTransformer('all-MiniLM-L6-v2')
            self.mode = "local-transformer"
            logging.info("VectorStore: Using local sentence-transformers ('all-MiniLM-L6-v2').")
        except ImportError:
            pass

        if self.openai_key:
            self.mode = "openai"
            logging.info("VectorStore: Using OpenAI embeddings ('text-embedding-3-small').")
            
        if self.mode == "tf-idf":
            logging.info("VectorStore: Using scikit-learn TF-IDF vectorizer fallback.")
            self.vectorizer = TfidfVectorizer(stop_words='english')
            self.vectors = None
            
        # Embedding caches for OpenAI / Local Transformer
        self.cached_embeddings: Dict[str, np.ndarray] = {}

    def _get_embedding(self, text: str) -> np.ndarray:
        if text in self.cached_embeddings:
            return self.cached_embeddings[text]
            
        if self.mode == "openai" and self.openai_key:
            try:
                import requests
                headers = {
                    "Authorization": f"Bearer {self.openai_key}",
                    "Content-Type": "application/json"
                }
                payload = {
                    "input": text[:8000],  # safety truncation
                    "model": "text-embedding-3-small"
                }
                res = requests.post("https://api.openai.com/v1/embeddings", headers=headers, json=payload, timeout=8)
                res.raise_for_status()
                emb = np.array(res.json()["data"][0]["embedding"], dtype=np.float32)
                self.cached_embeddings[text] = emb
                return emb
            except Exception as e:
                logging.warning(f"Failed to fetch OpenAI embedding: {str(e)}. Falling back to local/TF-IDF.")
                
        if self.mode == "local-transformer" and self.local_model:
            try:
                emb = self.local_model.encode(text)
                emb = np.array(emb, dtype=np.float32)
                self.cached_embeddings[text] = emb
                return emb
            except Exception as e:
                logging.warning(f"Failed to compute local transformer embedding: {str(e)}")
                
        # Zero-vector fallback if something fails or is running in TF-IDF mode
        return np.zeros(384) # size of L6-v2 embedding

    def add(self, memory: Memory):
        self.memories.append(memory)
        self._rebuild_index()

    def _rebuild_index(self):
        if not self.memories:
            return
            
        if self.mode == "tf-idf":
            corpus = [f"{m.content} {m.summary} {' '.join(m.tags)}" for m in self.memories]
            self.vectors = self.vectorizer.fit_transform(corpus)
        else:
            # Prefetch embeddings for all memories
            for m in self.memories:
                text = f"{m.content} {m.summary} {' '.join(m.tags)}"
                self._get_embedding(text)

    def search(self, query: str, top_k: int = 5) -> List[Tuple[Memory, float]]:
        if not self.memories:
            return []
            
        if self.mode == "tf-idf":
            if self.vectors is None:
                self._rebuild_index()
            if self.vectors is None:
                return []
            query_vec = self.vectorizer.transform([query])
            similarities = cosine_similarity(query_vec, self.vectors).flatten()
            
            top_indices = np.argsort(similarities)[::-1][:top_k]
            results = []
            for idx in top_indices:
                score = similarities[idx]
                if score > 0.01:
                    results.append((self.memories[idx], float(score)))
            return results
            
        # Semantic search using cosine similarity over embeddings
        query_emb = self._get_embedding(query)
        similarities = []
        
        for m in self.memories:
            text = f"{m.content} {m.summary} {' '.join(m.tags)}"
            mem_emb = self._get_embedding(text)
            
            # Compute cosine similarity
            dot_prod = np.dot(query_emb, mem_emb)
            norm_q = np.linalg.norm(query_emb)
            norm_m = np.linalg.norm(mem_emb)
            
            if norm_q > 0 and norm_m > 0:
                sim = dot_prod / (norm_q * norm_m)
            else:
                sim = 0.0
            similarities.append(float(sim))
            
        top_indices = np.argsort(similarities)[::-1][:top_k]
        results = []
        for idx in top_indices:
            score = similarities[idx]
            # Convert normal cosine similarity range [-1, 1] to positive score [0, 1]
            adjusted_score = max(0.0, float(score))
            if adjusted_score > 0.01:
                results.append((self.memories[idx], adjusted_score))
                
        return results
