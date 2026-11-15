import json, pathlib
import app, db, rag

ROWS = json.loads((pathlib.Path(__file__).parents[1] / "data" / "seed.json").read_text())


def call(monkeypatch, m, path, qs=None, body=None):
    monkeypatch.setattr(db, "investigations", lambda: ROWS)
    monkeypatch.setattr(db, "conditions", lambda i=None: [])
    monkeypatch.setattr(db, "search_chunks", lambda q, k=8: [{"id": None, "name": "NASA brief", "text": "Moon Base 30% O2", "rank": 1}])
    r = app.handler({"httpMethod": m, "path": path, "queryStringParameters": qs, "body": json.dumps(body) if body else None}, None)
    return r["statusCode"], r["headers"]["Content-Type"], r["body"]


def test_routes(monkeypatch):
    for p in ("/health", "/environments", "/meta", "/earth", "/equipment", "/hardware", "/coverage", "/investigations", "/investigations/bass"):
        assert call(monkeypatch, "GET", p)[0] == 200, p
    assert call(monkeypatch, "GET", "/investigations/nope")[0] == 404
    assert call(monkeypatch, "GET", "/investigations", {"o2_min": "abc"})[0] == 400


def test_meta_incidents_resources(monkeypatch):
    s, _, b = call(monkeypatch, "GET", "/meta")
    d = json.loads(b)
    assert s == 200 and len(d["incidents"]) == 3 and all(r["url"].startswith("https://") for r in d["resources"])


def test_compare(monkeypatch):
    s, _, b = call(monkeypatch, "GET", "/compare", {"ids": "bass,flex"})
    assert s == 200 and json.loads(b)["different_fields"]
    assert call(monkeypatch, "GET", "/compare", {"ids": "bass"})[0] == 400
    assert call(monkeypatch, "GET", "/compare", {"ids": "bass,zzz"})[0] == 400


def test_export(monkeypatch):
    s, ct, b = call(monkeypatch, "GET", "/export", {"format": "csv", "fuel": "solid"})
    assert s == 200 and ct == "text/csv" and b.splitlines()[0].startswith("id,name") and len(b.splitlines()) == 6
    s, _, b = call(monkeypatch, "GET", "/export", {"format": "json"})
    assert len(json.loads(b)) == 20
    assert call(monkeypatch, "GET", "/export", {"kind": "conditions"})[0] == 200
    assert call(monkeypatch, "GET", "/export", {"format": "xml"})[0] == 400


def test_chat_fallback_without_keys(monkeypatch):
    monkeypatch.delenv("GROQ_API_KEYS", raising=False)
    s, _, b = call(monkeypatch, "POST", "/chat", body={"question": "Moon Base oxygen?"})
    assert s == 200 and json.loads(b)["citations"][0]["name"] == "NASA brief"
    assert call(monkeypatch, "POST", "/chat", body={})[0] == 400
