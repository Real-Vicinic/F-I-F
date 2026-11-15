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
    assert s == 200 and ct == "text/csv" and b.splitlines()[0].startswith("id,name") and len(b.splitlines()) == 7
    s, _, b = call(monkeypatch, "GET", "/export", {"format": "json"})
    assert len(json.loads(b)) == 25
    assert call(monkeypatch, "GET", "/export", {"kind": "conditions"})[0] == 200
    assert call(monkeypatch, "GET", "/export", {"format": "xml"})[0] == 400


def test_chat_fallback_without_keys(monkeypatch):
    monkeypatch.delenv("GROQ_API_KEYS", raising=False)
    s, _, b = call(monkeypatch, "POST", "/chat", body={"question": "Moon Base oxygen?"})
    d = json.loads(b)
    assert s == 200 and d["citations"][0]["name"] == "NASA brief"
    assert d["source"] == "fallback" and d["error"] == "no_keys"
    assert call(monkeypatch, "POST", "/chat", body={})[0] == 400


class FakeResp:
    def __init__(self, status, payload=None, text=""):
        self.status_code, self._payload, self.text = status, payload or {}, text

    def json(self):
        return self._payload


def test_chat_uses_groq(monkeypatch):
    monkeypatch.setenv("GROQ_API_KEYS", "k1;k2")
    monkeypatch.delenv("GROQ_MODEL", raising=False)
    sent = {}

    def fake_post(url, headers, json, timeout):
        sent.update(json)
        return FakeResp(200, {"choices": [{"message": {"content": "CFI-G tested up to 85% O2 [CFI-G]"}}]})

    monkeypatch.setattr(rag.requests, "post", fake_post)
    s, _, b = call(monkeypatch, "POST", "/chat", body={"question": "Moon Base oxygen?"})
    d = json.loads(b)
    assert s == 200 and d["source"] == "groq" and "CFI-G" in d["answer"]
    assert sent["model"] == "openai/gpt-oss-120b"


def test_chat_reports_groq_http_error(monkeypatch):
    monkeypatch.setenv("GROQ_API_KEYS", "k1;k2")
    calls = []

    def fake_post(url, headers, json, timeout):
        calls.append(headers["Authorization"])
        return FakeResp(404, text='{"error":{"code":"model_not_found"}}')

    monkeypatch.setattr(rag.requests, "post", fake_post)
    s, _, b = call(monkeypatch, "POST", "/chat", body={"question": "Moon Base oxygen?"})
    d = json.loads(b)
    assert s == 200 and d["source"] == "fallback" and d["error"] == "http_404"
    assert len(calls) == 2  # tried every key


def test_chat_empty_groq_answer_falls_back(monkeypatch):
    monkeypatch.setenv("GROQ_API_KEYS", "k1")
    monkeypatch.setattr(rag.requests, "post", lambda *a, **k: FakeResp(200, {"choices": [{"message": {"content": ""}}]}))
    d = json.loads(call(monkeypatch, "POST", "/chat", body={"question": "Moon Base oxygen?"})[2])
    assert d["source"] == "fallback" and d["error"] == "empty_response"


def test_fallback_text_names_the_reason(monkeypatch):
    monkeypatch.setenv("GROQ_API_KEYS", "k1")
    monkeypatch.setenv("GROQ_MODEL", "llama-3.3-70b-versatile")
    monkeypatch.setattr(rag.requests, "post", lambda *a, **k: FakeResp(404, text="model_not_found"))
    d = json.loads(call(monkeypatch, "POST", "/chat", body={"question": "Moon Base oxygen?"})[2])
    assert d["answer"].startswith("SI model unavailable (Groq does not have model llama-3.3-70b-versatile)")
