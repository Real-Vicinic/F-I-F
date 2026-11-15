import { useMemo, useState } from "react";
import { FACTORS, DEFAULT_W, factors, blend, COVER } from "./rank.js";
import { Fits, Tags, State } from "./ui.jsx";
import FlameStage from "./FlameStage.jsx";
import Reference from "./Reference.jsx";

export function Panel({ title, right, open: initial = true, children, className = "" }) {
  const [open, setOpen] = useState(initial);
  return (
    <div className={`panel ${className}`}>
      <div className="phd">
        <button className="phead" aria-expanded={open} onClick={() => setOpen(!open)}>
          <h2>{title}</h2><span className={`chev${open ? " up" : ""}`} aria-hidden="true" />
        </button>
        {right}
      </div>
      {open && <div className="pbody">{children}</div>}
    </div>
  );
}

const Bar = ({ v }) => (
  <span className="sbar"><i style={{ width: `${v * 100}%` }} /></span>
);

function Weights({ w, setW }) {
  return (
    <Panel title="Ranking weights">
      {FACTORS.map((f) => (
        <label className="wrow" key={f.key} title={f.tip}>
          <span>{f.label}</span>
          <input type="range" min="0" max="1" step="0.05" value={w[f.key]} style={{ "--p": `${w[f.key] * 100}%` }}
            onChange={(e) => setW({ ...w, [f.key]: +e.target.value })} />
          <output>{w[f.key].toFixed(2)}</output>
        </label>
      ))}
    </Panel>
  );
}

function Detail({ x, w, picked, toggle }) {
  if (!x) return <Panel title="Experiment detail"><p className="dim">Select an experiment.</p></Panel>;
  return (
    <Panel title="Experiment detail">
      <h3 className="dname">{x.name} <span className="dim">{x.full_name}</span></h3>
      <Fits fits={x.fits} />
      <Tags tags={x.tags} />
      <p className="dobj">{x.objective}</p>
      <h4>Score breakdown</h4>
      {FACTORS.map((f) => (
        <div className="brow" key={f.key}>
          <span>{f.label}</span><Bar v={x.fx[f.key]} />
          <em>{x.fx[f.key].toFixed(2)} × {w[f.key].toFixed(2)}</em>
        </div>
      ))}
      <div className="dact">
        <a className="btn" href={`#/i/${x.id}`}>Full detail →</a>
        <label className="pick"><input type="checkbox" checked={picked.includes(x.id)} onChange={() => toggle(x.id)} /> Compare</label>
      </div>
    </Panel>
  );
}

function Ranked({ rows, sel, setSel, picked, toggle, f, set, scn }) {
  const active = f.scenario && scn[f.scenario];
  return (
    <Panel title="Ranked experiments" right={active && <button className="badge" onClick={() => set("scenario", "")}>{active.label} ✕</button>}>
      <div className="filters">
        <input placeholder="Filter by name, fuel, tag…" value={f.q} onChange={(e) => set("q", e.target.value)} />
        <select value={f.fuel} onChange={(e) => set("fuel", e.target.value)}>
          <option value="">All fuels</option><option value="solid">Solid</option><option value="liquid">Liquid</option>
          <option value="gas">Gas</option><option value="aerosol">Smoke / dust</option>
        </select>
        <select value={f.hardware} onChange={(e) => set("hardware", e.target.value)}>
          <option value="">All hardware</option><option value="CIR">CIR</option><option value="MDCA">MDCA</option><option value="MSG">MSG</option><option value="Saffire">Saffire</option>
        </select>
        <select value={f.tier} onChange={(e) => set("tier", e.target.value)}>
          <option value="">All tiers</option><option value="direct">Direct</option><option value="related">Related</option><option value="indirect">Indirect</option>
        </select>
        <select value={f.focus} onChange={(e) => set("focus", e.target.value)}>
          <option value="all">Focus: overall</option><option value="prevention">Focus: prevention</option>
          <option value="detection">Focus: detection</option><option value="suppression">Focus: suppression</option>
        </select>
      </div>
      {!rows.length ? <p className="dim">No investigations match these filters.</p> : (
        <div className="scroll">
          <table className="rtable">
            <thead><tr><th>#</th><th>Experiment</th><th>Platform</th><th>Tier</th><th>Score</th><th title="Select to compare">⇄</th></tr></thead>
            <tbody>
              {rows.map((r, n) => (
                <tr key={r.id} className={sel === r.id ? "sel" : ""} tabIndex={0} onClick={() => setSel(r.id)}
                  onKeyDown={(e) => e.key === "Enter" && setSel(r.id)}>
                  <td className="rk">{n + 1}{r.moved !== 0 && <small className={r.moved > 0 ? "up" : "dn"} title="Change vs default weights">{r.moved > 0 ? "▲" : "▼"}{Math.abs(r.moved)}</small>}</td>
                  <td><b>{r.name}</b><br /><span className="dim">{r.full_name}</span></td>
                  <td>{r.facility}</td>
                  <td className={`tier ${r.tier}`}>{r.tier}</td>
                  <td className="sc"><span>{r.s.toFixed(2)}</span><Bar v={r.s} /></td>
                  <td onClick={(e) => e.stopPropagation()}><input type="checkbox" aria-label={`Compare ${r.name}`} checked={picked.includes(r.id)} onChange={() => toggle(r.id)} /></td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </Panel>
  );
}

function Coverage({ rows, sel, setSel }) {
  return (
    <Panel title="Fire variable coverage">
      <div className="scroll">
        <table className="cov">
          <thead><tr><th>Experiment</th>{COVER.map(([k, name]) => <th key={k} title={name}>{k}</th>)}</tr></thead>
          <tbody>
            {rows.map((r) => (
              <tr key={r.id} className={sel === r.id ? "sel" : ""} onClick={() => setSel(r.id)}>
                <th>{r.name}</th>
                {COVER.map(([k, , test]) => <td key={k} className={test(r) ? "on" : ""}><i /></td>)}
              </tr>
            ))}
          </tbody>
        </table>
      </div>
      <p className="dim note">Orange = variable recorded or varied, derived from each investigation's variables, sensors and tags. Hover headers for names.</p>
    </Panel>
  );
}

const SHORT = { iss: "ISS", moon_base: "Moon", rover: "Rover", spacesuit: "Suit", spacecraft: "Craft", mars_base: "Mars" };

function O2Chart({ items, conds, scn }) {
  const rows = items.map((i) => {
    const pts = conds.filter((c) => c.investigation_id === i.id && c.o2_pct != null).map((c) => +c.o2_pct);
    const hi = Math.max(i.o2_max ?? -1, ...pts);
    return hi < 0 ? null : { i, lo: i.o2_min, hi, pts };
  }).filter(Boolean);
  const habs = {};
  Object.entries(scn).forEach(([k, e]) => { if (e.o2_pct) (habs[e.o2_pct] ||= []).push(SHORT[k] || k); });
  const W = 640, L = 118, R = 28, T = 30, H = T + rows.length * 22 + 26;
  const x = (v) => L + (v / 100) * (W - L - R);
  return (
    <svg className="o2" viewBox={`0 0 ${W} ${H}`} role="img" aria-label="Tested oxygen range per investigation against habitat oxygen levels">
      {[0, 20, 40, 60, 80, 100].map((t) => (
        <g key={t}><line className="grid" x1={x(t)} x2={x(t)} y1={T - 6} y2={H - 22} /><text className="tick" x={x(t)} y={H - 8} textAnchor="middle">{t}%</text></g>
      ))}
      {Object.entries(habs).map(([o2, names]) => (
        <g key={o2}>
          <line className="hab" x1={x(o2)} x2={x(o2)} y1={T - 6} y2={H - 22} />
          <text className="habt" x={x(o2)} y={T - 12} textAnchor={+o2 > 90 ? "end" : "middle"}>{names.join("/")} {o2}%</text>
        </g>
      ))}
      {rows.map((r, n) => {
        const y = T + n * 22 + 8;
        return (
          <g key={r.i.id}>
            <text className="lbl" x={L - 8} y={y + 4} textAnchor="end">{r.i.name}</text>
            {r.lo != null && r.lo !== r.hi
              ? <rect className="rng" x={x(r.lo)} y={y - 4} width={x(r.hi) - x(r.lo)} height="8" rx="4" />
              : <line className="upto" x1={x(0)} x2={x(r.hi)} y1={y} y2={y} />}
            <circle className="cap" cx={x(r.hi)} cy={y} r="4" />
            {r.pts.map((p, k) => <circle key={k} className="pt" cx={x(p)} cy={y} r="3.2" />)}
            <text className="val" x={x(r.hi) + 8} y={y + 4}>{r.lo != null && r.lo !== r.hi ? `${r.lo}–${r.hi}%` : `up to ${r.hi}%`}</text>
          </g>
        );
      })}
    </svg>
  );
}

function Environment({ items, conds, scn, f, set }) {
  const count = (k, v) => items.filter((i) => i.fits?.[k] === v).length;
  const active = f.scenario && scn[f.scenario];
  const desktop = typeof matchMedia === "function" && matchMedia("(min-width: 761px)").matches;
  return (
    <Panel title="Test conditions vs habitat atmospheres" open={desktop} className="env"
      right={active && <span className="badge static">{active.label}</span>}>
      <div className="chips">
        <button className={!f.scenario ? "on" : ""} onClick={() => set("scenario", "")}>All environments</button>
        {Object.entries(scn).map(([k, s]) => (
          <button key={k} className={f.scenario === k ? "on" : ""} onClick={() => set("scenario", k)}>
            {s.label}{s.o2_pct ? ` · ${s.o2_pct}% O₂ · ${s.psi} psi` : ""}
          </button>
        ))}
      </div>
      {active?.note && <p className="dim">{active.note}</p>}
      <div className="scroll">
        <table className="atm">
          <thead><tr><th>Habitat</th><th>O₂</th><th>Pressure</th><th>O₂ partial</th><th>Confirmed</th><th>Possible</th></tr></thead>
          <tbody>
            {Object.entries(scn).map(([k, s]) => (
              <tr key={k} className={f.scenario === k ? "sel" : ""} onClick={() => set("scenario", f.scenario === k ? "" : k)}>
                <th>{s.label}{s.basis === "assumed" ? <span className="dim"> (assumed)</span> : null}</th>
                <td>{s.o2_pct ? `${s.o2_pct}%` : "n/a"}</td><td>{s.psi ? `${s.psi} psi` : "n/a"}</td><td>{s.pp_o2_psi ? `${s.pp_o2_psi} psia` : "n/a"}</td>
                <td>{count(k, "confirmed")}</td><td>{count(k, "possible")}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
      <h4>Oxygen tested vs habitat oxygen</h4>
      <O2Chart items={items} conds={conds} scn={scn} />
      <p className="dim note">Bars show the oxygen range tested; dashed lines show habitat oxygen. Dashed bars have no recorded lower bound. Only investigations with oxygen data appear.</p>
    </Panel>
  );
}

export default function Explorer({ items, err, scn, conds, w, setW, picked, toggle }) {
  const [f, setF] = useState({ q: "", fuel: "", hardware: "", tier: "", scenario: "", focus: "all" });
  const [sel, setSel] = useState(null);
  const set = (k, v) => setF((p) => ({ ...p, [k]: v }));

  const rows = useMemo(() => {
    if (!items) return [];
    const terms = f.q.toLowerCase().split(/\s+/).filter(Boolean);
    const ctx = { focus: f.focus, scenario: f.scenario };
    const base = items.filter((i) => {
      if (f.fuel && i.fuel_type !== f.fuel) return false;
      if (f.tier && i.tier !== f.tier) return false;
      if (f.hardware && !`${i.hardware || ""} ${i.hardware_family || ""}`.toLowerCase().includes(f.hardware.toLowerCase())) return false;
      if (f.scenario && !["confirmed", "possible"].includes(i.fits?.[f.scenario])) return false;
      const blob = [i.name, i.full_name, i.family, i.fuel_type, i.fuels, i.hardware, i.facility, ...(i.tags || [])].join(" ").toLowerCase();
      return terms.every((t) => blob.includes(t));
    }).map((i) => {
      const fx = factors(i, ctx);
      return { ...i, fx, s: blend(fx, w), s0: blend(fx, DEFAULT_W) };
    });
    const order = (k) => [...base].sort((a, b) => b[k] - a[k] || a.name.localeCompare(b.name));
    const def = new Map(order("s0").map((r, n) => [r.id, n]));
    return order("s").map((r, n) => ({ ...r, moved: def.get(r.id) - n }));
  }, [items, f, w]);

  if (!items) return <State err={err} loading={!err} />;
  const picked1 = rows.find((r) => r.id === sel);

  return (
    <>
      <section className="chamber">
        <div>
          <h1>A flame behaves differently when nothing rises</h1>
          <p>What NASA microgravity combustion experiments reveal about preventing, detecting and putting out fires on the ISS, the Moon and Mars.</p>
        </div>
        <FlameStage />
      </section>
      <div className="dash">
        <div className="col left">
          <Ranked rows={rows} sel={sel} setSel={setSel} picked={picked} toggle={toggle} f={f} set={set} scn={scn} />
          <Coverage rows={rows} sel={sel} setSel={setSel} />
          <Environment items={items} conds={conds} scn={scn} f={f} set={set} />
        </div>
        <div className="col right">
          <Weights w={w} setW={setW} />
          <Detail x={picked1} w={w} picked={picked} toggle={toggle} />
          <Panel title="Fire physics reference"><Reference /></Panel>
        </div>
      </div>
      <div className="panel info">
        <h3>Partial gravity — data coming soon</h3>
        <p className="dim">PSI has no partial-gravity combustion data yet. LUCI and FM2 are expected to add Moon-gravity results; E-FIELD Flames mimics partial gravity with electric fields in the meantime.</p>
      </div>
    </>
  );
}
