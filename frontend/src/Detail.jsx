import { useEffect, useState } from "react";
import { get, post } from "./api.js";
import { Score, Fits, Tags, State } from "./ui.jsx";

export default function Detail({ id }) {
  const [d, setD] = useState(null);
  const [err, setErr] = useState(null);
  const [why, setWhy] = useState(null);
  const [busy, setBusy] = useState(false);

  useEffect(() => {
    setD(null); setWhy(null); setErr(null);
    get(`/investigations/${id}`).then(setD).catch((e) => setErr(e.message));
  }, [id]);

  const explain = () => {
    setBusy(true);
    post("/chat", { question: `Why does ${d.name} matter for fire safety in crewed space environments such as the Moon Base?`, investigation_id: id })
      .then(setWhy).catch((e) => setWhy({ answer: `SI unavailable (${e.message})`, citations: [] })).finally(() => setBusy(false));
  };

  if (!d) return <State err={err} loading />;
  const rows = [["PSI ID", d.psi_id || "not specified"], ["Fuel type", d.fuel_type], ["Relevance tier", d.tier], ["Fuels", d.fuels], ["Sample / burner geometry", d.fuel_geometry || "not specified"], ["Hardware", d.hardware], ["Facility", d.facility],
    ["Oxygen", d.o2_note || "not specified"], ["Airflow", d.airflow || "not specified"], ["Gravity", d.gravity],
    ["Same across tests", `${d.same.hardware}; ${d.same.facility}; ${d.same.gravity}`], ["Varied across tests", d.varied?.join(", ")], ["Informs", d.informs?.join(", ")], ["Sensors", d.sensors?.join(", ")]];
  return (
    <div className="card detail">
      <a href="#/">← Back</a>
      <h2>{d.name} <span className="dim">{d.full_name}</span></h2>
      <Score v={d.score} /><Fits fits={d.fits} /><Tags tags={d.tags} />
      <p>{d.objective}</p>
      <table><tbody>{rows.map(([k, v]) => <tr key={k}><th>{k}</th><td>{v}</td></tr>)}</tbody></table>
      {d.conditions?.length > 0 && <p><b>Loaded test conditions:</b> {d.conditions.map((c) => `O₂ ${c.o2_pct ?? "?"}%, ${c.pressure_psi ?? "?"} psi, ${c.airflow_cm_s ?? "?"} cm/s`).join(" · ")}</p>}
      {d.earth_application && <p><b>On Earth:</b> {d.earth_application}</p>}
      <h3>Why it matters for fire safety</h3>
      {why ? <p className="answer">{why.answer}</p> : <button onClick={explain} disabled={busy}>{busy ? "Thinking…" : "Explain with SI"}</button>}
      <h3>Similar investigations</h3>
      <div className="tags">{d.similar.map((s) => <a key={s.id} href={`#/i/${s.id}`}>{s.name}</a>)}</div>
      <p className="dim">Source: <a href={d.source_url} target="_blank" rel="noreferrer">NASA PSI</a> · curated summary, verify values in PSI.</p>
    </div>
  );
}
