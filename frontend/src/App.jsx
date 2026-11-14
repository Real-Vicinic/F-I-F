import { useEffect, useState } from "react";
import { get } from "./api.js";
import { Score, Fits, Tags, State } from "./ui.jsx";
import Detail from "./Detail.jsx";
import Compare from "./Compare.jsx";
import Chat from "./Chat.jsx";
import Insights from "./Insights.jsx";

function useHash() {
  const [h, setH] = useState(location.hash.slice(1));
  useEffect(() => {
    const f = () => setH(location.hash.slice(1));
    addEventListener("hashchange", f);
    return () => removeEventListener("hashchange", f);
  }, []);
  return h;
}

function Explorer({ picked, toggle }) {
  const [f, setF] = useState({ q: "", fuel: "", hardware: "", tier: "", scenario: "", focus: "all" });
  const [data, setData] = useState(null);
  const [err, setErr] = useState(null);
  const [scn, setScn] = useState({});
  const set = (k, v) => setF((p) => ({ ...p, [k]: v }));

  useEffect(() => { get("/scenarios").then(setScn).catch(() => {}); }, []);
  useEffect(() => {
    setErr(null);
    const t = setTimeout(() => get("/investigations", f).then(setData).catch((e) => setErr(e.message)), 250);
    return () => clearTimeout(t);
  }, [f]);

  return (
    <>
      <div className="chips">
        <button className={!f.scenario ? "on" : ""} onClick={() => set("scenario", "")}>All environments</button>
        {Object.entries(scn).map(([k, s]) => (
          <button key={k} className={f.scenario === k ? "on" : ""} onClick={() => set("scenario", k)}>
            {s.label}{s.o2_pct ? ` · ${s.o2_pct}% O₂ · ${s.psi} psi` : ""}
          </button>
        ))}
      </div>
      {scn[f.scenario]?.note && <p className="dim">{scn[f.scenario].note}</p>}
      <div className="filters">
        <input placeholder="Search objectives, fuels, hardware…" value={f.q} onChange={(e) => set("q", e.target.value)} />
        <select value={f.fuel} onChange={(e) => set("fuel", e.target.value)}>
          <option value="">All fuels</option>
          <option value="solid">Solid</option><option value="liquid">Liquid</option>
          <option value="gas">Gas</option><option value="aerosol">Smoke / dust</option>
        </select>
        <select value={f.hardware} onChange={(e) => set("hardware", e.target.value)}>
          <option value="">All hardware</option>
          <option value="CIR">CIR</option><option value="MDCA">MDCA</option><option value="MSG">MSG</option><option value="Saffire">Saffire</option>
        </select>
        <select value={f.tier} onChange={(e) => set("tier", e.target.value)}>
          <option value="">All relevance tiers</option><option value="direct">Direct</option><option value="related">Related</option><option value="indirect">Indirect</option>
        </select>
        <select value={f.focus} onChange={(e) => set("focus", e.target.value)}>
          <option value="all">Rank: overall</option><option value="prevention">Rank: prevention</option>
          <option value="detection">Rank: detection</option><option value="suppression">Rank: suppression</option>
        </select>
      </div>
      <State err={err} loading={!data && !err} />
      {data && !data.items.length && <p className="dim">No investigations match these filters.</p>}
      <div className="grid">
        {data?.items.map((i) => (
          <div className="card" key={i.id}>
            <label className="pick" title="Select to compare">
              <input type="checkbox" checked={picked.includes(i.id)} onChange={() => toggle(i.id)} /> compare
            </label>
            <a href={`#/i/${i.id}`}><h3>{i.name}</h3></a>
            <p className="dim">{i.full_name}</p>
            <Score v={i.score} />
            <p className="meta">{i.tier} · {i.fuel_type} · {i.facility}<br />O₂: {i.o2_note || "n/a"}</p>
            <Fits fits={i.fits} />
            <Tags tags={i.tags} />
          </div>
        ))}
      </div>
      <div className="card info">
        <h3>Partial gravity — data coming soon</h3>
        <p className="dim">PSI has no partial-gravity combustion data yet. LUCI and FM2 are expected to add Moon-gravity results; E-FIELD Flames mimics partial gravity with electric fields in the meantime.</p>
      </div>
    </>
  );
}

export default function App() {
  const h = useHash();
  const [picked, setPicked] = useState([]);
  const toggle = (id) => setPicked((p) => (p.includes(id) ? p.filter((x) => x !== id) : [...p, id].slice(-2)));
  const [, a, b] = h.match(/^\/compare\/([\w-]+)\/([\w-]+)$/) || [];
  const dm = h.match(/^\/i\/([\w-]+)$/);

  return (
    <div className="wrap">
      <header>
        <a href="#/"><h1>🔥 Flame in Freefall</h1></a>
        <p className="dim">SI-powered fire safety insights from NASA microgravity combustion data (PSI)</p>
        <nav><a href="#/">Explorer</a> · <a href="#/insights">Insights</a></nav>
      </header>
      {h === "/insights" ? <Insights /> : a ? <Compare a={a} b={b} /> : dm ? <Detail id={dm[1]} /> : <Explorer picked={picked} toggle={toggle} />}
      {picked.length === 2 && !a && (
        <a className="comparebar" href={`#/compare/${picked[0]}/${picked[1]}`}>Compare {picked[0]} vs {picked[1]} →</a>
      )}
      <Chat />
    </div>
  );
}
