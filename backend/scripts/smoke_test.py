"""Post-deploy / scheduled smoke test. Usage: API_URL=https://... python smoke_test.py  (SMOKE_CHAT=1 also tests /chat)"""
import json, os, sys, time, urllib.error, urllib.request

BASE = (os.environ.get("API_URL") or (sys.argv[1] if len(sys.argv) > 1 else "")).rstrip("/")
if not BASE:
    sys.exit("API_URL missing")


def call(path, method="GET", body=None, headers=None):
    req = urllib.request.Request(BASE + path, method=method, headers={"User-Agent": "smoke", **(headers or {})},
                                 data=json.dumps(body).encode() if body else None)
    if body:
        req.add_header("Content-Type", "application/json")
    try:
        with urllib.request.urlopen(req, timeout=25) as r:
            return r.status, r.headers, r.read().decode()
    except urllib.error.HTTPError as e:
        return e.code, e.headers, e.read().decode()


def js(path, **kw):
    s, _, b = call(path, **kw)
    assert s == 200, f"{path} -> {s}"
    return json.loads(b)


for i in range(6):
    try:
        if call("/health")[0] == 200:
            break
    except OSError:
        pass
    time.sleep(5)

results = []


def check(name, fn):
    try:
        fn()
        results.append((name, None))
    except Exception as e:
        results.append((name, repr(e)))


def t_list():
    d = js("/investigations")
    assert d["total"] >= 20, d["total"]


def t_latency():
    t = time.time()
    js("/investigations")
    assert time.time() - t < 2.0, f"{time.time() - t:.2f}s"


def t_moon():
    assert "cfi-g" in [i["id"] for i in js("/investigations?scenario=moon_base")["items"]]


def t_detail():
    d = js("/investigations/bass")
    assert d["similar"] and d["same"]


def t_compare():
    assert js("/compare?ids=bass,flex")["different_fields"]


def t_export():
    s, h, b = call("/export?format=csv")
    assert s == 200 and "text/csv" in h.get("Content-Type", "") and b.startswith("id,name"), s


def t_env():
    assert len(js("/environments")) == 6


def t_cors():
    s, h, _ = call("/investigations", "OPTIONS", headers={"Origin": "https://example.com", "Access-Control-Request-Method": "GET"})
    assert s in (200, 204) and h.get("Access-Control-Allow-Origin"), (s, dict(h))


def t_chat():
    d = js("/chat", method="POST", body={"question": "Which investigations inform smoke detection?"})
    assert d["answer"] and d["citations"]


for name, fn in [("health", lambda: js("/health")["ok"]), ("list >= 20", t_list), ("list latency < 2s", t_latency),
                 ("moon_base includes CFI-G", t_moon), ("detail + similar", t_detail), ("compare", t_compare),
                 ("export csv", t_export), ("environments", t_env), ("coverage", lambda: js("/coverage")),
                 ("equipment", lambda: js("/equipment")), ("earth", lambda: js("/earth")), ("cors preflight", t_cors)]:
    check(name, fn)
if os.environ.get("SMOKE_CHAT") == "1":
    check("chat", t_chat)

failed = [r for r in results if r[1]]
for n, e in results:
    print(("FAIL " if e else "ok   ") + n + (f"  {e}" if e else ""))
sys.exit(1 if failed else 0)
