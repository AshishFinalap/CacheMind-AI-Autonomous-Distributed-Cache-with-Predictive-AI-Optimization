from flask import Blueprint, jsonify, request


def create_routes(cache_engine, predictor, semantic_index, diagnostics):
    bp = Blueprint("routes", __name__)

    @bp.post("/cache/set")
    def set_key():
        data = request.get_json(force=True)
        key = data["key"]
        value = data["value"]

        result = cache_engine.set(key, value)
        predictor.record_access(key)

        if isinstance(value, str):
            semantic_index.add(key, value)

        return jsonify({"ok": True, "result": result})

    @bp.get("/cache/get")
    def get_key():
        key = request.args.get("key")
        if not key:
            return jsonify({"ok": False, "error": "key is required"}), 400

        value = cache_engine.get(key)
        predictor.record_access(key)

        if value is None:
            return jsonify({"ok": False, "error": "not found"}), 404

        return jsonify({"ok": True, "key": key, "value": value})

    @bp.get("/cache/stats")
    def cache_stats():
        return jsonify({"ok": True, "stats": cache_engine.stats()})

    @bp.post("/cache/semantic/query")
    def semantic_query():
        data = request.get_json(force=True)
        text = data.get("text", "")
        top_k = int(data.get("top_k", 3))
        matches = semantic_index.query(text, top_k=top_k)
        return jsonify({"ok": True, "matches": matches})

    @bp.get("/diagnostics/cluster")
    def cluster_diagnostics():
        return jsonify({"ok": True, "diagnostics": diagnostics.cluster_status()})

    @bp.post("/diagnostics/query")
    def diagnostics_query():
        data = request.get_json(force=True)
        question = data.get("question", "")
        response = diagnostics.answer_question(question)
        return jsonify({"ok": True, "response": response})

    return bp
