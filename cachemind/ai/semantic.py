from difflib import SequenceMatcher
from typing import List, Tuple


class SemanticCacheIndex:
    def __init__(self, model_name: str = "sentence-transformers/all-MiniLM-L6-v2"):
        self.texts: List[str] = []
        self.keys: List[str] = []
        self.index = None
        self._fallback = False

        try:
            import faiss
            from sentence_transformers import SentenceTransformer

            self._faiss = faiss
            self.model = SentenceTransformer(model_name)
        except Exception:
            self._fallback = True
            self._faiss = None
            self.model = None

    def _ensure_index(self, dim: int):
        if self.index is None and not self._fallback:
            self.index = self._faiss.IndexFlatL2(dim)

    def add(self, key: str, text: str):
        self.keys.append(key)
        self.texts.append(text)

        if self._fallback:
            return

        emb = self.model.encode([text]).astype("float32")
        self._ensure_index(emb.shape[1])
        self.index.add(emb)

    def query(self, text: str, top_k: int = 3) -> List[Tuple[str, float]]:
        if len(self.keys) == 0:
            return []

        if self._fallback:
            scored = []
            for key, candidate_text in zip(self.keys, self.texts):
                ratio = SequenceMatcher(None, text.lower(), candidate_text.lower()).ratio()
                scored.append((key, 1.0 - ratio))
            scored.sort(key=lambda item: item[1])
            return scored[:top_k]

        q = self.model.encode([text]).astype("float32")
        distances, indices = self.index.search(q, top_k)
        results = []
        for dist, idx in zip(distances[0], indices[0]):
            if idx < 0 or idx >= len(self.keys):
                continue
            results.append((self.keys[idx], float(dist)))
        return results
