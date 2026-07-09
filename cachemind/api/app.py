from flask import Flask, render_template_string

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

    @app.get("/")
    def home():
        return render_template_string(
                        """
                        <!doctype html>
                        <html lang="en">
                        <head>
                            <meta charset="utf-8" />
                            <meta name="viewport" content="width=device-width, initial-scale=1" />
                            <title>CacheMind AI</title>
                            <style>
                                :root {
                                    color-scheme: dark;
                                    --bg: #08101f;
                                    --bg2: #111b34;
                                    --panel: rgba(15, 23, 42, 0.84);
                                    --panel-soft: rgba(15, 23, 42, 0.64);
                                    --panel-border: rgba(148, 163, 184, 0.2);
                                    --text: #e2e8f0;
                                    --muted: #94a3b8;
                                    --accent: #7dd3fc;
                                    --accent-2: #34d399;
                                    --warn: #fbbf24;
                                }

                                * { box-sizing: border-box; }
                                html { scroll-behavior: smooth; }
                                body {
                                    margin: 0;
                                    min-height: 100vh;
                                    font-family: Inter, Segoe UI, Arial, sans-serif;
                                    color: var(--text);
                                    background:
                                        radial-gradient(circle at top left, rgba(125, 211, 252, 0.22), transparent 30%),
                                        radial-gradient(circle at 85% 15%, rgba(52, 211, 153, 0.16), transparent 24%),
                                        linear-gradient(160deg, var(--bg), var(--bg2));
                                }

                                .shell {
                                    max-width: 1180px;
                                    margin: 0 auto;
                                    padding: 40px 20px 56px;
                                }

                                .hero {
                                    display: grid;
                                    grid-template-columns: minmax(0, 1.3fr) minmax(320px, 0.9fr);
                                    gap: 24px;
                                    align-items: start;
                                    margin-bottom: 22px;
                                }

                                .eyebrow {
                                    display: inline-flex;
                                    align-items: center;
                                    gap: 10px;
                                    padding: 8px 14px;
                                    border-radius: 999px;
                                    border: 1px solid var(--panel-border);
                                    background: rgba(255, 255, 255, 0.04);
                                    color: var(--muted);
                                    letter-spacing: 0.09em;
                                    text-transform: uppercase;
                                    font-size: 12px;
                                }

                                h1 {
                                    margin: 16px 0 12px;
                                    font-size: clamp(42px, 7vw, 74px);
                                    line-height: 0.93;
                                    letter-spacing: -0.06em;
                                }

                                .lede {
                                    margin: 0;
                                    max-width: 64ch;
                                    color: var(--muted);
                                    font-size: 18px;
                                    line-height: 1.7;
                                }

                                .actions {
                                    display: flex;
                                    flex-wrap: wrap;
                                    gap: 12px;
                                    margin-top: 24px;
                                }

                                .button {
                                    appearance: none;
                                    display: inline-flex;
                                    align-items: center;
                                    justify-content: center;
                                    padding: 12px 18px;
                                    border-radius: 14px;
                                    border: 1px solid var(--panel-border);
                                    color: var(--text);
                                    text-decoration: none;
                                    background: rgba(255, 255, 255, 0.05);
                                    transition: transform 160ms ease, background 160ms ease, border-color 160ms ease;
                                    cursor: pointer;
                                }

                                .button.primary {
                                    background: linear-gradient(135deg, rgba(125, 211, 252, 0.24), rgba(52, 211, 153, 0.18));
                                    border-color: rgba(125, 211, 252, 0.34);
                                }

                                .button:hover { transform: translateY(-1px); }
                                .button:active { transform: translateY(0); }

                                .panel,
                                .card,
                                .result {
                                    border: 1px solid var(--panel-border);
                                    background: var(--panel);
                                    box-shadow: 0 24px 80px rgba(0, 0, 0, 0.26);
                                    backdrop-filter: blur(16px);
                                }

                                .panel {
                                    border-radius: 24px;
                                    padding: 20px;
                                }

                                .metric {
                                    display: grid;
                                    gap: 4px;
                                    padding: 16px 0;
                                    border-bottom: 1px solid rgba(148, 163, 184, 0.12);
                                }

                                .metric:last-child { border-bottom: 0; padding-bottom: 0; }
                                .metric-label {
                                    color: var(--muted);
                                    font-size: 12px;
                                    text-transform: uppercase;
                                    letter-spacing: 0.08em;
                                }
                                .metric-value { font-size: 22px; font-weight: 700; }
                                .metric-sub { color: var(--muted); font-size: 13px; line-height: 1.5; }

                                .grid {
                                    display: grid;
                                    grid-template-columns: repeat(12, minmax(0, 1fr));
                                    gap: 16px;
                                    margin-top: 22px;
                                }

                                .card {
                                    grid-column: span 6;
                                    border-radius: 22px;
                                    padding: 18px;
                                }

                                .card.full { grid-column: 1 / -1; }
                                .card h2 {
                                    margin: 0 0 12px;
                                    font-size: 16px;
                                    letter-spacing: 0.02em;
                                }

                                .section-copy {
                                    margin: 0 0 16px;
                                    color: var(--muted);
                                    line-height: 1.6;
                                    font-size: 14px;
                                }

                                .form-grid {
                                    display: grid;
                                    grid-template-columns: repeat(2, minmax(0, 1fr));
                                    gap: 12px;
                                }

                                .field {
                                    display: grid;
                                    gap: 7px;
                                }

                                .field.full { grid-column: 1 / -1; }
                                .field label {
                                    color: var(--muted);
                                    font-size: 12px;
                                    text-transform: uppercase;
                                    letter-spacing: 0.08em;
                                }

                                input, textarea {
                                    width: 100%;
                                    border-radius: 14px;
                                    border: 1px solid rgba(148, 163, 184, 0.18);
                                    background: rgba(2, 6, 23, 0.55);
                                    color: var(--text);
                                    padding: 12px 14px;
                                    outline: none;
                                    font: inherit;
                                }

                                textarea {
                                    min-height: 94px;
                                    resize: vertical;
                                }

                                input:focus, textarea:focus {
                                    border-color: rgba(125, 211, 252, 0.52);
                                    box-shadow: 0 0 0 3px rgba(125, 211, 252, 0.12);
                                }

                                .result {
                                    border-radius: 18px;
                                    padding: 14px;
                                    margin-top: 14px;
                                    min-height: 112px;
                                    background: var(--panel-soft);
                                    white-space: pre-wrap;
                                    word-break: break-word;
                                    color: #dbeafe;
                                    line-height: 1.55;
                                }

                                .result[data-empty="true"] {
                                    color: var(--muted);
                                }

                                .pill-row {
                                    display: flex;
                                    flex-wrap: wrap;
                                    gap: 8px;
                                    margin: 8px 0 0;
                                }

                                .pill {
                                    padding: 6px 10px;
                                    border-radius: 999px;
                                    background: rgba(255, 255, 255, 0.05);
                                    border: 1px solid rgba(148, 163, 184, 0.16);
                                    color: var(--muted);
                                    font-size: 12px;
                                }

                                .table {
                                    display: grid;
                                    gap: 8px;
                                }

                                .row {
                                    display: grid;
                                    grid-template-columns: 180px 1fr;
                                    gap: 10px;
                                    padding: 12px 14px;
                                    border-radius: 14px;
                                    background: rgba(255, 255, 255, 0.04);
                                    border: 1px solid rgba(148, 163, 184, 0.12);
                                }

                                .row span:first-child {
                                    color: var(--muted);
                                    text-transform: uppercase;
                                    letter-spacing: 0.08em;
                                    font-size: 12px;
                                }

                                .footer-note {
                                    margin-top: 16px;
                                    color: var(--muted);
                                    font-size: 13px;
                                    line-height: 1.6;
                                }

                                @media (max-width: 920px) {
                                    .hero,
                                    .card,
                                    .form-grid,
                                    .row {
                                        grid-template-columns: 1fr;
                                    }

                                    .card { grid-column: 1 / -1; }
                                }
                            </style>
                        </head>
                        <body>
                            <main class="shell">
                                <section class="hero">
                                    <div>
                                        <div class="eyebrow">CacheMind AI live control surface</div>
                                        <h1>Predictive cache infrastructure, running locally.</h1>
                                        <p class="lede">
                                            This project is a demo distributed cache: set values, read them back from replica nodes,
                                            inspect diagnostics, and search text payloads semantically. The UI below exercises the actual API.
                                        </p>
                                        <div class="actions">
                                            <button class="button primary" type="button" onclick="scrollToSection('cache-form')">Try the cache</button>
                                            <button class="button" type="button" onclick="refreshAll()">Refresh live state</button>
                                            <a class="button" href="/health">Health</a>
                                        </div>
                                        <div class="pill-row">
                                            <span class="pill">Flask API</span>
                                            <span class="pill">Consistent hashing</span>
                                            <span class="pill">Replica-aware cache</span>
                                            <span class="pill">Diagnostics engine</span>
                                            <span class="pill">Semantic query fallback</span>
                                        </div>
                                    </div>

                                    <aside class="panel">
                                        <div class="metric">
                                            <div class="metric-label">Service</div>
                                            <div class="metric-value">CacheMind AI</div>
                                            <div class="metric-sub">The app is responding on port 5000 and serving the live demo UI.</div>
                                        </div>
                                        <div class="metric">
                                            <div class="metric-label">API surface</div>
                                            <div class="metric-value">/cache • /diagnostics</div>
                                            <div class="metric-sub">Use the browser forms below to hit the real routes.</div>
                                        </div>
                                        <div class="metric">
                                            <div class="metric-label">Runtime state</div>
                                            <div class="metric-value" id="runtime-state">Loading…</div>
                                            <div class="metric-sub" id="runtime-substate">Checking cache and cluster status.</div>
                                        </div>
                                    </aside>
                                </section>

                                <section class="grid">
                                    <article class="card full" id="cache-form">
                                        <h2>Cache operations</h2>
                                        <p class="section-copy">Write a key, read it back, and see how the replicated cache reacts.</p>
                                        <div class="form-grid">
                                            <div class="field">
                                                <label for="set-key">Set key</label>
                                                <input id="set-key" placeholder="user:1" value="user:1" />
                                            </div>
                                            <div class="field">
                                                <label for="set-value">Set value</label>
                                                <input id="set-value" placeholder='{"name":"ashish"}' value='{"name":"ashish"}' />
                                            </div>
                                            <div class="field full">
                                                <button class="button primary" type="button" onclick="setCache()">Store key</button>
                                            </div>
                                            <div class="field">
                                                <label for="get-key">Get key</label>
                                                <input id="get-key" placeholder="user:1" value="user:1" />
                                            </div>
                                            <div class="field">
                                                <label>&nbsp;</label>
                                                <button class="button" type="button" onclick="getCache()">Fetch key</button>
                                            </div>
                                        </div>
                                        <div class="result" id="cache-result" data-empty="true">No cache action yet.</div>
                                    </article>

                                    <article class="card">
                                        <h2>Diagnostics</h2>
                                        <p class="section-copy">Inspect active nodes, hot keys, and the recommended policy from the runtime engine.</p>
                                        <div class="field">
                                            <label for="diagnostics-question">Ask a diagnostic question</label>
                                            <textarea id="diagnostics-question">Why is latency high on node-2?</textarea>
                                        </div>
                                        <div class="actions" style="margin-top: 12px;">
                                            <button class="button primary" type="button" onclick="getCluster()">Cluster status</button>
                                            <button class="button" type="button" onclick="askDiagnostics()">Ask question</button>
                                        </div>
                                        <div class="result" id="diagnostics-result" data-empty="true">No diagnostic result yet.</div>
                                    </article>

                                    <article class="card">
                                        <h2>Semantic lookup</h2>
                                        <p class="section-copy">If you store text values, the semantic index can return approximate matches.</p>
                                        <div class="field">
                                            <label for="semantic-text">Query text</label>
                                            <textarea id="semantic-text">ashish profile cache entry</textarea>
                                        </div>
                                        <div class="actions" style="margin-top: 12px;">
                                            <button class="button primary" type="button" onclick="semanticQuery()">Search</button>
                                        </div>
                                        <div class="result" id="semantic-result" data-empty="true">No semantic search yet.</div>
                                    </article>

                                    <article class="card full">
                                        <h2>Live state</h2>
                                        <p class="section-copy">The dashboard refreshes the current cache stats and cluster diagnostics from the API.</p>
                                        <div class="table">
                                            <div class="row"><span>Cache stats</span><span id="cache-stats">Loading…</span></div>
                                            <div class="row"><span>Cluster diagnostics</span><span id="cluster-stats">Loading…</span></div>
                                        </div>
                                        <div class="footer-note">
                                            The TCP heartbeat port is part of the MVP architecture, but it will remain idle until a node client sends a heartbeat message.
                                        </div>
                                    </article>
                                </section>
                            </main>

                            <script>
                                const emptyState = (el, text) => {
                                    el.textContent = text;
                                    el.dataset.empty = 'true';
                                };

                                const setState = (el, payload) => {
                                    el.textContent = typeof payload === 'string' ? payload : JSON.stringify(payload, null, 2);
                                    el.dataset.empty = 'false';
                                };

                                const parseMaybeJson = (value) => {
                                    const trimmed = value.trim();
                                    if (!trimmed) {
                                        return '';
                                    }

                                    try {
                                        return JSON.parse(trimmed);
                                    } catch (error) {
                                        return trimmed;
                                    }
                                };

                                const fetchJson = async (url, options) => {
                                    const response = await fetch(url, {
                                        headers: { 'Content-Type': 'application/json' },
                                        ...options,
                                    });
                                    const text = await response.text();
                                    let payload;
                                    try {
                                        payload = text ? JSON.parse(text) : {};
                                    } catch (error) {
                                        payload = { raw: text };
                                    }

                                    if (!response.ok) {
                                        throw new Error(payload.error || response.statusText || 'Request failed');
                                    }

                                    return payload;
                                };

                                async function refreshAll() {
                                    await Promise.all([refreshStats(), refreshCluster()]);
                                }

                                async function refreshStats() {
                                    const stats = await fetchJson('/cache/stats');
                                    const nodes = stats.stats.nodes || [];
                                    const items = stats.stats.items_per_node || {};
                                    const count = Object.values(items).reduce((total, value) => total + value, 0);
                                    document.getElementById('cache-stats').textContent = `${count} item(s) across ${nodes.length} node(s); replication factor ${stats.stats.replication_factor}.`;
                                    document.getElementById('runtime-state').textContent = `${count} cached item(s)`;
                                    document.getElementById('runtime-substate').textContent = nodes.length ? `Ring members: ${nodes.join(', ')}` : 'The ring is initialized but contains no stored items yet.';
                                }

                                async function refreshCluster() {
                                    const cluster = await fetchJson('/diagnostics/cluster');
                                    const d = cluster.diagnostics;
                                    const active = d.active_nodes && d.active_nodes.length ? d.active_nodes.join(', ') : 'none';
                                    const hotKeys = d.hot_keys && d.hot_keys.length ? d.hot_keys.join(', ') : 'none';
                                    document.getElementById('cluster-stats').textContent = `Active nodes: ${active}; hot keys: ${hotKeys}; policy: ${d.recommended_policy}.`;
                                }

                                async function setCache() {
                                    const key = document.getElementById('set-key').value.trim();
                                    const value = parseMaybeJson(document.getElementById('set-value').value);
                                    const result = await fetchJson('/cache/set', {
                                        method: 'POST',
                                        body: JSON.stringify({ key, value }),
                                    });
                                    setState(document.getElementById('cache-result'), result);
                                    await refreshAll();
                                }

                                async function getCache() {
                                    const key = document.getElementById('get-key').value.trim();
                                    const result = await fetchJson(`/cache/get?key=${encodeURIComponent(key)}`);
                                    setState(document.getElementById('cache-result'), result);
                                }

                                async function getCluster() {
                                    const result = await fetchJson('/diagnostics/cluster');
                                    setState(document.getElementById('diagnostics-result'), result);
                                    await refreshCluster();
                                }

                                async function askDiagnostics() {
                                    const question = document.getElementById('diagnostics-question').value.trim();
                                    const result = await fetchJson('/diagnostics/query', {
                                        method: 'POST',
                                        body: JSON.stringify({ question }),
                                    });
                                    setState(document.getElementById('diagnostics-result'), result);
                                }

                                async function semanticQuery() {
                                    const text = document.getElementById('semantic-text').value.trim();
                                    const result = await fetchJson('/cache/semantic/query', {
                                        method: 'POST',
                                        body: JSON.stringify({ text, top_k: 5 }),
                                    });
                                    setState(document.getElementById('semantic-result'), result);
                                }

                                function scrollToSection(id) {
                                    document.getElementById(id).scrollIntoView({ behavior: 'smooth', block: 'start' });
                                }

                                window.refreshAll = refreshAll;
                                window.setCache = setCache;
                                window.getCache = getCache;
                                window.getCluster = getCluster;
                                window.askDiagnostics = askDiagnostics;
                                window.semanticQuery = semanticQuery;
                                window.scrollToSection = scrollToSection;

                                refreshAll().catch((error) => {
                                    emptyState(document.getElementById('cache-stats'), `Unable to load cache stats: ${error.message}`);
                                    emptyState(document.getElementById('cluster-stats'), `Unable to load cluster diagnostics: ${error.message}`);
                                });
                            </script>
                        </body>
                        </html>
                        """
                )

    @app.get("/health")
    def health():
        return {"ok": True, "service": "cachemind-ai"}

    return app
