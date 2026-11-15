import os, random, re
import requests
import db

STOP = set("the a an of and or to in on for is are was were which what how why that this with at by from as be it do does did "
           "tests test experiments experiment investigations investigation ran run".split())
SYSTEM = ("You are the SI assistant for a NASA microgravity combustion fire-safety dashboard. Answer ONLY from the provided context. "
          "Cite investigation names in square brackets, e.g. [BASS]. If the context does not contain the answer, say you don't know "
          "based on the indexed data. If a value is not specified in the context, say so. Be concise.")


def terms(q):
    ws = re.findall(r"[a-z0-9]+", q.lower().replace("\u2082", "2"))
    return list(dict.fromkeys(w for w in ws if len(w) > 1 and w not in STOP))


def retrieve(q, k=8):
    t = terms(q)
    return db.search_chunks(" | ".join(t), k) if t else []


DEFAULT_MODEL = "openai/gpt-oss-120b"  # llama-3.3-70b-versatile was shut down by Groq on 2026-08-16


def _groq(messages):
    """Returns (answer, error). answer is None when every key failed; error says why."""
    keys = [k for k in re.split(r"[,;\s]+", os.environ.get("GROQ_API_KEYS", "")) if k]
    if not keys:
        print("groq: GROQ_API_KEYS is empty")
        return None, "no_keys"
    model = os.environ.get("GROQ_MODEL") or DEFAULT_MODEL
    random.shuffle(keys)
    err = "unknown"
    for key in keys:
        try:
            r = requests.post("https://api.groq.com/openai/v1/chat/completions",
                              headers={"Authorization": f"Bearer {key}"},
                              json={"model": model, "messages": messages, "temperature": 0.2,
                                    "max_tokens": 1000, "reasoning_effort": "low"}, timeout=8)
            if r.status_code == 200:
                text = (r.json()["choices"][0]["message"].get("content") or "").strip()
                if text:
                    return text, None
                err = "empty_response"
                print("groq: empty content from", model)
            else:
                err = f"http_{r.status_code}"
                print("groq error", r.status_code, model, r.text[:200])
        except (requests.RequestException, ValueError, KeyError, IndexError) as e:
            err = "request_failed"
            print("groq exception", repr(e))
    return None, err


def _reason(err):
    """Human-readable cause shown in the chat when Groq could not answer."""
    model = os.environ.get("GROQ_MODEL") or DEFAULT_MODEL
    return {
        "no_keys": "GROQ_API_KEYS is not set on the server",
        "http_401": "Groq rejected the API key",
        "http_403": "Groq blocked the request (403)",
        "http_404": f"Groq does not have model {model}",
        "http_400": f"Groq rejected the request for model {model}",
        "http_429": "Groq rate limit reached",
        "request_failed": "could not reach Groq (timeout or network error)",
        "empty_response": f"model {model} returned an empty answer",
    }.get(err, f"Groq error {err}")


def ask(question, inv_id=None):
    question = question.strip()[:500]
    ctx = db.inv_chunks(inv_id) if inv_id else retrieve(question)
    if not ctx:
        return {"answer": "I don't know based on the indexed PSI metadata.", "citations": []}
    cites = list({c["id"] or c["name"]: {"id": c["id"], "name": c["name"]} for c in ctx}.values())
    context = "\n".join(f"[{c['name']}] {c['text']}" for c in ctx)
    answer, err = _groq([{"role": "system", "content": SYSTEM},
                         {"role": "user", "content": f"Context:\n{context}\n\nQuestion: {question}"}])
    if answer is None:
        facts = "\n".join(f"- {c['text']}" for c in ctx[:4])
        answer = f"SI model unavailable ({_reason(err)}). Relevant indexed facts:\n" + facts
        return {"answer": answer, "citations": cites, "source": "fallback", "error": err}
    return {"answer": answer, "citations": cites, "source": "groq"}
