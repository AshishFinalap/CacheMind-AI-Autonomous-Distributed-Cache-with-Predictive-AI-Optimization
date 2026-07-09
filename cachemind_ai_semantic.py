from typing import List, Tuple

import faiss
from sentence_transformers import SentenceTransformer


class SemanticCacheIndex:
    def __init__(self, model_name: str = "sentence-transformers/all-MiniLM-L6-v2"):
        self.model = SentenceTransformer(model_name)
        self.texts: List[str] = []
        self.keys: List[str] = []
        self.index = None

    def _ensure_index(self, dim: int):
        if self.index is None:
            self.index = faiss.IndexFlatL2(dim)

    def add(self, key: str, text: str):
        emb = self.model.encode([text]).astype("float32")
        self._ensure_index(emb.shape[1])
        self.index.add(emb)
        self.keys.append(key)
        self.texts.append(text)

    def query(self, text: str, top_k: int = 3) -> List[Tuple[str, float]]:
        if self.index is None or len(self.keys) == 0:
            return []
        q = self.model.encode([text]).astype("float32")
        distances, indices = self.index.search(q, top_k)
        results = []
        for dist, idx in zip(distances[0], indices[0]):
            if idx < 0 or idx >= len(self.keys):
                continue
            results.append((self.keys[idx], float(dist)))
        return results