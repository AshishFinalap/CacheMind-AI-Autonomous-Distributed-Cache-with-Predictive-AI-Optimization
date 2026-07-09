# CacheMind AI

CacheMind AI is a small but complete demo of a distributed in-memory cache with a live browser dashboard, API endpoints, consistent hashing, replica placement, simple diagnostics, and an AI-flavored access predictor.

The project is intentionally lightweight and educational rather than production hardened. It shows how a cache service can be split into a core engine, a network layer, observability, and a web UI that exercises the real routes.

## What it does

- Stores key/value pairs in a replica-aware cache ring
- Routes keys through consistent hashing with virtual nodes
- Tracks access frequency to detect hot keys and suggest a policy
- Exposes diagnostics for cluster state and natural-language-style questions
- Supports semantic lookup for text payloads when the optional ML stack is available
- Provides a browser dashboard for trying the API without leaving the app

## Live Demo

When the app is running, open:

- `http://127.0.0.1:5000/` for the dashboard
- `http://127.0.0.1:5000/health` for uptime
- `http://127.0.0.1:5000/cache/stats` for cache state
- `http://127.0.0.1:5000/diagnostics/cluster` for cluster diagnostics

The dashboard includes forms to:

- set a key and value
- read a key back
- ask diagnostics questions
- run semantic queries
- refresh live cache and cluster status

## Architecture

The runtime is split into four main pieces:

- `cachemind/core/` contains the consistent-hash ring and cache engine
- `cachemind/ai/` contains the access predictor and semantic search index
- `cachemind/network/` contains the TCP heartbeat messenger
- `cachemind/observability/` contains the diagnostics engine
- `cachemind/api/` contains the Flask app, routes, and dashboard

At startup, the app creates three nodes, a replication factor of 2, a predictor, a semantic index, and a TCP messenger on port 9000. The web server itself runs on port 5000.

## Tech Stack

- Python 3.10+
- Flask
- scikit-learn
- sentence-transformers
- faiss-cpu
- TCP sockets
- Docker and docker-compose

## Project Layout

```text
cachemind/
  api/
    app.py
    routes.py
  ai/
    predictor.py
    semantic.py
  core/
    engine.py
    ring.py
  network/
    tcp_layer.py
  observability/
    diagnostics.py
run.py
requirements.txt
docker-compose.yml
Dockerfile.txt
```

## Run Locally

```bash
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -r requirements.txt
python run.py
```

Then open `http://127.0.0.1:5000/`.

## Run With Docker

```bash
docker compose up --build
```

## API Reference

### Cache

`POST /cache/set`

Request body:

```json
{
  "key": "user:1",
  "value": {"name": "ashish"}
}
```

Example:

```bash
curl -X POST http://127.0.0.1:5000/cache/set \
  -H "Content-Type: application/json" \
  -d '{"key":"user:1","value":{"name":"ashish"}}'
```

`GET /cache/get?key=user:1`

```bash
curl "http://127.0.0.1:5000/cache/get?key=user:1"
```

`GET /cache/stats`

```bash
curl "http://127.0.0.1:5000/cache/stats"
```

### Diagnostics

`GET /diagnostics/cluster`

```bash
curl "http://127.0.0.1:5000/diagnostics/cluster"
```

`POST /diagnostics/query`

```bash
curl -X POST http://127.0.0.1:5000/diagnostics/query \
  -H "Content-Type: application/json" \
  -d '{"question":"Why is latency high on node-2?"}'
```

### Semantic Search

`POST /cache/semantic/query`

```bash
curl -X POST http://127.0.0.1:5000/cache/semantic/query \
  -H "Content-Type: application/json" \
  -d '{"text":"ashish profile cache entry","top_k":3}'
```

## How the Demo Works

The homepage is not static marketing content. It is a live control panel that calls the real API routes from the browser.

- Setting a key stores the value in the replica-aware cache engine
- Reading a key checks the replica nodes in order and returns the first match
- Every access updates the predictor history, which drives hot-key detection and the suggested policy
- Diagnostic queries inspect the current cache ring, active TCP heartbeats, and hot keys
- Semantic queries use the text index when the optional ML dependencies are available, and fall back to a simpler matching strategy when they are not

## Limitations

This is a demo system, not a production cache platform.

- Heartbeat traffic is stubbed unless a node client sends messages to port 9000
- Failover is represented as diagnostics and routing primitives, not a real orchestrator
- Semantic search depends on large optional Python packages and may fall back to a lightweight text matcher if the full stack is unavailable
- Data is in-memory and disappears when the process restarts

## Troubleshooting

- If the app does not start, make sure you installed the Python dependencies listed in `requirements.txt`
- If the semantic index fails to load, the app still runs with the fallback matcher
- If port 5000 is already in use, stop the process using it before running `python run.py`
- If the dashboard shows no active nodes, that is expected until a TCP heartbeat client connects on port 9000

## Roadmap

- Add real worker-node processes
- Implement replication synchronization and automated failover
- Persist cache state to a durable backend
- Expand the semantic search layer with production-ready embeddings
- Add tests for cache behavior, diagnostics, and dashboard interactions

## License

No license file is currently included. Add one before distributing or accepting external contributions.
