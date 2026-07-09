# CacheMind AI — Autonomous Distributed Cache with Predictive AI Optimization

CacheMind AI is an MVP distributed in-memory cache demonstrating:

- Consistent hashing with virtual nodes
- Multi-node replication-ready key placement
- Basic failover-aware routing primitives
- AI optimization hooks for hot-key detection and policy recommendation
- Semantic cache lookup scaffolding with FAISS + sentence embeddings
- Observability endpoints and lightweight diagnostics

## Tech Stack

- Python 3.10+
- Flask
- TCP sockets (node heartbeat/client messaging stubs)
- scikit-learn
- sentence-transformers
- faiss-cpu
- Docker + docker-compose

## Project Structure

- `cachemind/core/` — ring, cache engine, replication logic
- `cachemind/ai/` — predictor, anomaly/hot-key detector, semantic index
- `cachemind/observability/` — diagnostics and metrics
- `cachemind/network/` — TCP messaging and node heartbeats
- `cachemind/api/` — Flask app and routes

## Quick Start (Local)

```bash
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -r requirements.txt
python run.py
```

Server starts at: `http://127.0.0.1:5000`

Open the root page in a browser to use the interactive dashboard:

- `http://127.0.0.1:5000/` for the UI
- `http://127.0.0.1:5000/health` for uptime
- `http://127.0.0.1:5000/cache/stats` for cache state
- `http://127.0.0.1:5000/diagnostics/cluster` for cluster diagnostics

## Quick Start (Docker)

```bash
docker compose up --build
```

## Sample API Calls

Set key:

```bash
curl -X POST http://127.0.0.1:5000/cache/set \
  -H "Content-Type: application/json" \
  -d '{"key":"user:1","value":{"name":"ashish"}}'
```

Get key:

```bash
curl "http://127.0.0.1:5000/cache/get?key=user:1"
```

Cluster diagnostics:

```bash
curl "http://127.0.0.1:5000/diagnostics/cluster"
```

Natural language diagnostics:

```bash
curl -X POST http://127.0.0.1:5000/diagnostics/query \
  -H "Content-Type: application/json" \
  -d '{"question":"Why is latency high on node-2?"}'
```

## Notes

This is an MVP scaffold designed for iterative enhancement:

- Add real multi-process worker nodes
- Wire true network replication and automatic failover election
- Improve ML training loop with production traffic traces
- Extend semantic retrieval from keys to payload metadata
