class DiagnosticsEngine:
    def __init__(self, cache_engine, predictor, tcp_messenger):
        self.cache_engine = cache_engine
        self.predictor = predictor
        self.tcp_messenger = tcp_messenger

    def cluster_status(self) -> dict:
        return {
            "cache": self.cache_engine.stats(),
            "active_nodes": self.tcp_messenger.active_nodes(),
            "hot_keys": self.predictor.hot_keys(),
            "recommended_policy": self.predictor.recommend_policy(),
        }

    def answer_question(self, question: str) -> dict:
        q = question.lower()
        status = self.cluster_status()

        if "latency" in q:
            return {
                "question": question,
                "answer": "Latency spikes usually correlate with hot keys or node imbalance. Check hot_keys and replication distribution.",
                "status": status,
            }
        if "failover" in q:
            return {
                "question": question,
                "answer": "Failover readiness depends on active replica nodes and replication factor coverage.",
                "status": status,
            }

        return {
            "question": question,
            "answer": "Cluster appears healthy in MVP diagnostics. For deeper RCA, integrate tracing and p99 latency timelines.",
            "status": status,
        }