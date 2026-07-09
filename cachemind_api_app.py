from flask import Flask

from cachemind.ai import AccessPredictor, SemanticCacheIndex
from cachemind.api.routes import create_routes
from cachemind.core import CacheEngine
from cachemind.network import TCPMessenger
from cachemind.observability import DiagnosticsEngine


def create_app() -> Flask:
    app = Flask(__name__)

    nodes = ["node-1", "node-2", "node-3"]
    cache_engine = CacheEngine(nodes=nodes, replication_factor=2)
    predictor = AccessPredictor()
    semantic_index = SemanticCacheIndex()

    messenger = TCPMessenger(host="0.0.0.0", port=9000)
    messenger.start()

    diagnostics = DiagnosticsEngine(
        cache_engine=cache_engine,
        predictor=predictor,
        tcp_messenger=messenger,
    )

    app.register_blueprint(create_routes(cache_engine, predictor, semantic_index, diagnostics))

    @app.get("/health")
    def health():
        return {"ok": True, "service": "cachemind-ai"}

    return app