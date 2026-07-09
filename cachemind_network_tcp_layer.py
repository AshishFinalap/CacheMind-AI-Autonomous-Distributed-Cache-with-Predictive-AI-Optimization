import json
import socket
import threading
from dataclasses import dataclass
from time import time


@dataclass
class NodeHeartbeat:
    node_id: str
    last_seen: float


class TCPMessenger:
    def __init__(self, host: str = "0.0.0.0", port: int = 9000):
        self.host = host
        self.port = port
        self.server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.heartbeats: dict[str, NodeHeartbeat] = {}

    def start(self):
        self.server.bind((self.host, self.port))
        self.server.listen(20)
        threading.Thread(target=self._accept_loop, daemon=True).start()

    def _accept_loop(self):
        while True:
            client, _ = self.server.accept()
            threading.Thread(target=self._handle_client, args=(client,), daemon=True).start()

    def _handle_client(self, client: socket.socket):
        try:
            data = client.recv(4096).decode("utf-8")
            message = json.loads(data)
            if message.get("type") == "heartbeat":
                node_id = message.get("node_id", "unknown")
                self.heartbeats[node_id] = NodeHeartbeat(node_id=node_id, last_seen=time())
            client.sendall(json.dumps({"status": "ok"}).encode("utf-8"))
        except Exception:
            pass
        finally:
            client.close()

    def active_nodes(self, timeout_seconds: int = 10) -> list[str]:
        now = time()
        return [nid for nid, hb in self.heartbeats.items() if now - hb.last_seen <= timeout_seconds]