import { useEffect, useState } from "react";
import { get } from "./api.js";
import { State } from "./ui.jsx";

const show = (v) => (Array.isArray(v) ? v.join(", ") : v ?? "not specified");

export default function Compare({ a, b }) {
  const [d, setD] = useState(null);
  const [err, setErr] = useState(null);
  useEffect(() => {
    setD(null);
    get("/compare", { ids: `${a},${b}` }).then(setD).catch((e) => setErr(e.message));
  }, [a, b]);
  if (!d) return <State err={err} loading />;
  return (
    <div className="card detail">
      <a href="#/">← Back</a>
      <table>
        <thead><tr><th></th>{d.investigations.map((r) => <th key={r.id}><a href={`#/i/${r.id}`}>{r.name}</a> <span className="dim">({r.score})</span></th>)}</tr></thead>
        <tbody>{d.fields.map((f) => (
          <tr key={f.field} className={f.same ? "" : "diff"}>
            <th>{f.label}</th>{d.investigations.map((r) => <td key={r.id}>{show(f.values[r.id])}</td>)}
          </tr>
        ))}</tbody>
      </table>
      <p><b>Similar:</b> {d.same_fields.join(", ") || "nothing"}. {d.shared_tags.length > 0 && <>Shared tags: {d.shared_tags.join(", ")}.</>}</p>
      <p><b>Different:</b> {d.different_fields.join(", ") || "nothing"}.</p>
    </div>
  );
}
