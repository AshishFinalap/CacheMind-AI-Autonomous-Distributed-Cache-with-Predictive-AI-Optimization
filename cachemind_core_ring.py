import hashlib
from bisect import bisect_right
from typing import Dict, List


class ConsistentHashRing:
    def __init__(self, nodes: List[str] | None = None, virtual_nodes: int = 50):
        self.virtual_nodes = virtual_nodes
        self.ring: Dict[int, str] = {}
        self.sorted_keys: List[int] = []
        self.nodes = set()

        if nodes:
            for node in nodes:
                self.add_node(node)

    @staticmethod
    def _hash(value: str) -> int:
        return int(hashlib.md5(value.encode("utf-8")).hexdigest(), 16)

    def add_node(self, node: str) -> None:
        if node in self.nodes:
            return
        self.nodes.add(node)
        for i in range(self.virtual_nodes):
            vnode_key = self._hash(f"{node}#{i}")
            self.ring[vnode_key] = node
            self.sorted_keys.append(vnode_key)
        self.sorted_keys.sort()

    def remove_node(self, node: str) -> None:
        if node not in self.nodes:
            return
        self.nodes.remove(node)
        remove_keys = [k for k, n in self.ring.items() if n == node]
        for k in remove_keys:
            del self.ring[k]
            self.sorted_keys.remove(k)

    def get_node(self, key: str) -> str:
        if not self.ring:
            raise RuntimeError("No nodes in hash ring")
        key_hash = self._hash(key)
        idx = bisect_right(self.sorted_keys, key_hash)
        if idx == len(self.sorted_keys):
            idx = 0
        vnode = self.sorted_keys[idx]
        return self.ring[vnode]

    def get_n_nodes(self, key: str, n: int = 2) -> List[str]:
        if not self.ring:
            return []
        key_hash = self._hash(key)
        idx = bisect_right(self.sorted_keys, key_hash)
        if idx == len(self.sorted_keys):
            idx = 0

        selected = []
        seen = set()
        i = idx
        while len(selected) < min(n, len(self.nodes)):
            vnode = self.sorted_keys[i]
            node = self.ring[vnode]
            if node not in seen:
                selected.append(node)
                seen.add(node)
            i = (i + 1) % len(self.sorted_keys)

        return selected