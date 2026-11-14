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


def _groq(messages):
    keys = [k for k in re.split(r"[,;\s]+", os.environ.get("GROQ_API_KEYS", "")) if k]
    random.shuffle(keys)
    for key in keys:
        try:
            r = requests.post("https://api.groq.com/openai/v1/chat/completions",
                              headers={"Authorization": f"Bearer {key}"},
                              json={"model": os.environ.get("GROQ_MODEL", "llama-3.3-70b-versatile"),
                                    "messages": messages, "temperature": 0.2, "max_tokens": 600}, timeout=18)
            if r.status_code == 200:
                return r.json()["choices"][0]["message"]["content"]
        except requests.RequestException:
            pass
    return None


def ask(question, inv_id=None):
    question = question.strip()[:500]
    ctx = db.inv_chunks(inv_id) if inv_id else retrieve(question)
    if not ctx:
        return {"answer": "I don't know based on the indexed PSI metadata.", "citations": []}
    cites = list({c["id"] or c["name"]: {"id": c["id"], "name": c["name"]} for c in ctx}.values())
    context = "\n".join(f"[{c['name']}] {c['text']}" for c in ctx)
    answer = _groq([{"role": "system", "content": SYSTEM},
                    {"role": "user", "content": f"Context:\n{context}\n\nQuestion: {question}"}])
    if answer is None:
        answer = "SI model unavailable. Relevant indexed facts:\n" + "\n".join(f"- {c['text']}" for c in ctx[:4])
    return {"answer": answer, "citations": cites}
