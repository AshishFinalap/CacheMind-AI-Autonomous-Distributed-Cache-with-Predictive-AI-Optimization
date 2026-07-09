from collections import defaultdict
from dataclasses import dataclass
from typing import Any, Dict

from cachemind.core.ring import ConsistentHashRing


@dataclass
class CacheItem:
    key: str
    value: Any
    access_count: int = 0


class CacheEngine:
    def __init__(self, nodes: list[str], replication_factor: int = 2):
        self.ring = ConsistentHashRing(nodes=nodes, virtual_nodes=100)
        self.replication_factor = replication_factor
        self.storage: Dict[str, Dict[str, CacheItem]] = defaultdict(dict)

    def set(self, key: str, value: Any) -> dict:
        target_nodes = self.ring.get_n_nodes(key, self.replication_factor)
        for node in target_nodes:
            self.storage[node][key] = CacheItem(key=key, value=value)
        return {"key": key, "replicated_to": target_nodes}

    def get(self, key: str) -> Any:
        target_nodes = self.ring.get_n_nodes(key, self.replication_factor)
        for node in target_nodes:
            item = self.storage[node].get(key)
            if item:
                item.access_count += 1
                return item.value
        return None

    def stats(self) -> dict:
        return {
            "nodes": list(self.ring.nodes),
            "items_per_node": {n: len(v) for n, v in self.storage.items()},
            "replication_factor": self.replication_factor,
        }
