import { useEffect, useMemo, useState } from "react";
import { analyze } from "./gaps.js";
import { get } from "./api.js";
import { DEFAULT_W } from "./rank.js";
import Explorer from "./Explorer.jsx";
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

export default function App() {
  const h = useHash();
  const [picked, setPicked] = useState([]);
  const toggle = (id) => setPicked((p) => (p.includes(id) ? p.filter((x) => x !== id) : [...p, id].slice(-2)));
  const [items, setItems] = useState(null);
  const [err, setErr] = useState(null);
  const [scn, setScn] = useState({});
  const [conds, setConds] = useState([]);
  const [w, setW] = useState(DEFAULT_W);

  useEffect(() => {
    get("/investigations", { limit: 100 }).then((d) => setItems(d.items)).catch((e) => setErr(e.message));
    get("/scenarios").then(setScn).catch(() => {});
    get("/conditions").then((d) => setConds(d.items || [])).catch(() => {});
  }, []);

  const gaps = useMemo(() => analyze(items, conds), [items, conds]);
  const [, a, b] = h.match(/^\/compare\/([\w-]+)\/([\w-]+)$/) || [];
  const dm = h.match(/^\/i\/([\w-]+)$/);
  const explorer = h !== "/insights" && !a && !dm;
  const api = err ? ["off", "API: offline"] : items ? ["ok", "API: live"] : ["", "API: connecting"];

  return (
    <div className="wrap">
      <header className="bar">
        <a className="brand" href="#/">Flame in <b>Freefall</b></a>
        <span className={`pill ${api[0]}`}>{api[1]}</span>
        {items && <><span className="pill">{items.length} experiments</span><span className="pill">{items.filter((i) => i.tier === "direct").length} direct</span>
          <span className={`pill${gaps.updated ? " ok" : ""}`} title="Experiments whose oxygen, pressure or airflow gaps were filled from NASA sources">{gaps.updated} gaps updated</span>
          <span className="pill" title="Experiments still missing oxygen, pressure or airflow">{gaps.withOpen} with open gaps</span></>}
        {explorer && <button className="rerank" title="Reset the sliders to the default weights" onClick={() => setW(DEFAULT_W)}>Re-rank</button>}
      </header>
      <nav className="tabs">
        <a href="#/" className={h === "/insights" ? "" : "on"}>Explorer</a>
        <a href="#/insights" className={h === "/insights" ? "on" : ""}>Insights</a>
      </nav>
      {h === "/insights" ? <Insights /> : a ? <Compare a={a} b={b} /> : dm ? <Detail id={dm[1]} /> : (
        <Explorer items={items} err={err} scn={scn} conds={conds} w={w} setW={setW} picked={picked} toggle={toggle} />
      )}
      {picked.length === 2 && !a && (
        <a className="comparebar" href={`#/compare/${picked[0]}/${picked[1]}`}>Compare {picked[0]} vs {picked[1]} →</a>
      )}
      <Chat />
    </div>
  );
}
