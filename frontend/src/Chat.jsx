import { useRef, useState } from "react";
import { post } from "./api.js";

const DEMO = [
  "Which experiments tested materials at 30%+ oxygen like the planned Moon Base?",
  "Which investigations inform smoke detection?",
  "How was fire suppression tested in microgravity?",
];

export default function Chat() {
  const [open, setOpen] = useState(false);
  const [msgs, setMsgs] = useState([]);
  const [q, setQ] = useState("");
  const [busy, setBusy] = useState(false);
  const end = useRef();

  const send = async (text) => {
    if (!text.trim() || busy) return;
    setMsgs((m) => [...m, { role: "user", text }]); setQ(""); setBusy(true);
    try {
      const r = await post("/chat", { question: text });
      setMsgs((m) => [...m, { role: "ai", text: r.answer, cites: r.citations }]);
    } catch (e) {
      setMsgs((m) => [...m, { role: "ai", text: `Error: ${e.message}`, cites: [] }]);
    }
    setBusy(false);
    setTimeout(() => end.current?.scrollIntoView({ behavior: "smooth" }), 50);
  };

  if (!open) return <button className="fab" onClick={() => setOpen(true)}>Ask SI</button>;
  return (
    <aside className="drawer">
      <div className="dhead"><b>SI assistant</b><button onClick={() => setOpen(false)}>✕</button></div>
      <div className="msgs">
        {!msgs.length && DEMO.map((d) => <button key={d} className="demo" onClick={() => send(d)}>{d}</button>)}
        {msgs.map((m, i) => (
          <div key={i} className={`msg ${m.role}`}>
            <p>{m.text}</p>
            {m.cites?.length > 0 && <div className="tags">{m.cites.map((c) => c.id ? <a key={c.id} href={`#/i/${c.id}`} onClick={() => setOpen(false)}>{c.name}</a> : <span key={c.name}>{c.name}</span>)}</div>}
          </div>
        ))}
        {busy && <p className="dim">Thinking…</p>}
        <div ref={end} />
      </div>
      <form onSubmit={(e) => { e.preventDefault(); send(q); }}>
        <input value={q} onChange={(e) => setQ(e.target.value)} placeholder="Ask about the indexed data…" />
        <button disabled={busy}>Send</button>
      </form>
    </aside>
  );
}
