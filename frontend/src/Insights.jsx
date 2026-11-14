import { useEffect, useState } from "react";
import { get, BASE } from "./api.js";
import { State } from "./ui.jsx";

const link = (i) => (i.id ? <a key={i.id} href={`#/i/${i.id}`}>{i.name}</a> : <span key={i.name}>{i.name}</span>);

export default function Insights() {
  const [d, setD] = useState(null);
  const [err, setErr] = useState(null);
  useEffect(() => {
    Promise.all([get("/environments"), get("/coverage"), get("/equipment"), get("/earth"), get("/meta"), get("/hardware")])
      .then(([env, cov, eq, earth, meta, hw]) => setD({ env, cov, eq, earth, meta, hw })).catch((e) => setErr(e.message));
  }, []);
  if (!d) return <State err={err} loading />;
  const { env, cov, eq, earth, meta, hw } = d;
  const ex = (q) => `${BASE}/export?${q}`;
  return (
    <>
      <section className="card">
        <h2>Crew environments</h2>
        <table>
          <thead><tr><th>Environment</th><th>O₂</th><th>Pressure</th><th>O₂ partial pressure</th><th>Prevention</th><th>Detection</th><th>Suppression</th></tr></thead>
          <tbody>{Object.entries(env).map(([k, e]) => (
            <tr key={k}>
              <td><b>{e.label}</b><br /><span className="dim">{e.note}{e.basis === "assumed" ? " (assumed)" : ""}</span></td>
              <td>{e.o2_pct ? `${e.o2_pct}%` : "n/a"}</td><td>{e.psi ? `${e.psi} psi` : "n/a"}</td><td>{e.pp_o2_psi ? `${e.pp_o2_psi} psia` : "n/a"}</td>
              {["prevention", "detection", "suppression"].map((f) => (
                <td key={f}><div className="tags">{cov.environments[k].by_function[f].slice(0, 4).map((i) => <a key={i.id} href={`#/i/${i.id}`}>{i.name}</a>)}</div></td>
              ))}
            </tr>
          ))}</tbody>
        </table>
        <p className="dim">Investigations shown have confirmed or possible oxygen coverage for that environment, ordered by strength for each function.</p>
      </section>

      <section className="card">
        <h2>Next-generation fire safety controls and equipment</h2>
        {Object.entries(eq).map(([k, a]) => (
          <div key={k}><h3>{k.replace("_", " ")}</h3><p className="dim">{a.description}</p>
            <div className="tags">{a.investigations.map((i) => <a key={i.id} href={`#/i/${i.id}`}>{i.name}</a>)}</div></div>
        ))}
      </section>

      <section className="card">
        <h2>Applications on Earth</h2>
        {earth.items.map((x) => (
          <p key={x.id}><b>{x.title}</b> — {x.origin}. {x.earth_use}.{" "}
            {x.related.length > 0 && <span className="tags">{x.related.map(link)}</span>}</p>
        ))}
      </section>

      <section className="card">
        <h2>Hardware families</h2>
        {Object.entries(hw).map(([k, g]) => (
          <p key={k}><b>{k}</b> <span className="dim">{g.hardware}</span><span className="tags">{g.investigations.map(link)}</span></p>
        ))}
      </section>

      <section className="card">
        <h2>Gaps in the data</h2>
        <ul>{[...cov.static_gaps.map((g) => `${g.title}. ${g.detail}`), ...cov.computed_gaps].map((g) => <li key={g}>{g}</li>)}</ul>
      </section>

      <section className="card">
        <h2>Data for predictive modeling</h2>
        <p className="dim">Flattened investigation metadata and any loaded test conditions. Raw measurements stay in <a href={meta.psi_url} target="_blank" rel="noreferrer">NASA PSI</a>.</p>
        <div className="tags">
          <a href={ex("format=csv")}>Investigations CSV</a><a href={ex("format=json")}>Investigations JSON</a>
          <a href={ex("kind=conditions&format=csv")}>Test conditions CSV</a><a href={ex("kind=conditions&format=json")}>Test conditions JSON</a>
        </div>
        <p className="dim">Audience: {meta.audience.join(", ")}.</p>
      </section>
    </>
  );
}
