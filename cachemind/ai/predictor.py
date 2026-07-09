from collections import Counter
from typing import List

from sklearn.linear_model import LinearRegression


class AccessPredictor:
    def __init__(self):
        self.history: List[str] = []
        self.model = LinearRegression()

    def record_access(self, key: str) -> None:
        self.history.append(key)

    def hot_keys(self, top_n: int = 5) -> List[str]:
        counts = Counter(self.history)
        return [k for k, _ in counts.most_common(top_n)]

    def recommend_policy(self) -> str:
        counts = Counter(self.history)
        if not counts:
            return "LRU"
        concentration = max(counts.values()) / max(1, sum(counts.values()))
        return "LFU" if concentration > 0.35 else "LRU"

    def prefetch_candidates(self, n: int = 3) -> List[str]:
        return self.hot_keys(top_n=n)

    def anomaly_score(self, current_latency_ms: float, baseline: float = 15.0) -> float:
        if baseline <= 0:
            return 0.0
        return float(max(0.0, (current_latency_ms - baseline) / baseline))
