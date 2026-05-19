import numpy as np
from typing import List, Tuple
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from chrona.schemas.memory import Memory

class VectorStore:
    def __init__(self):
        self.vectorizer = TfidfVectorizer(stop_words='english')
        self.memories: List[Memory] = []
        self.vectors = None

    def add(self, memory: Memory):
        self.memories.append(memory)
        self._rebuild_index()

    def _rebuild_index(self):
        if not self.memories:
            self.vectors = None
            return
        
        corpus = [f"{m.content} {m.summary} {' '.join(m.tags)}" for m in self.memories]
        self.vectors = self.vectorizer.fit_transform(corpus)

    def search(self, query: str, top_k: int = 5) -> List[Tuple[Memory, float]]:
        if not self.memories or self.vectors is None:
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
