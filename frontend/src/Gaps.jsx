import { useState } from "react";
import { FIELDS } from "./gaps.js";
import { Panel } from "./Explorer.jsx";

const LABEL = { updated: "Updated", partial: "Partly updated", open: "Open", complete: "Complete" };
const FILTERS = [["all", "All"], ["updated", "Updated"], ["open", "Open gaps"], ["verify", "Verify in PSI"]];

const Dot = ({ r, k, label }) => {
  const s = r.base[k] ? "have" : r.now[k] ? "new" : "none";
  const t = { have: "in the original record", new: "filled from a NASA source", none: "still unknown" }[s];
  return <td><span className={`gdot ${s}`} title={`${label}: ${t}`} /></td>;
};

export default function Gaps({ gaps, sel, setSel }) {
  const [f, setF] = useState("all");
  const show = gaps.rows.filter((r) =>
    f === "updated" ? r.filled.length : f === "open" ? r.open.length : f === "verify" ? r.verify : true);
  return (
    <Panel title="Data gaps" right={gaps.updated > 0 && <span className="badge static">{gaps.updated} updated</span>}>
      <div className="gstats">
        {FIELDS.map(([k, label]) => {
          const t = gaps.totals[k], d = t.now - t.base;
          return (
            <div className="gstat" key={k}>
              <span className="dim">{label}</span>
              <b>{t.now}<small> / {t.total}</small></b>
              <span className="sbar"><i style={{ width: `${(t.now / t.total) * 100}%` }} /></span>
              <em className={d ? "up" : "dim"}>{d ? `+${d} filled` : "no change"} <span className="dim">(was {t.base})</span></em>
            </div>
          );
        })}
      </div>
      <div className="chips">
        {FILTERS.map(([k, label]) => <button key={k} className={f === k ? "on" : ""} onClick={() => setF(k)}>{label}</button>)}
      </div>
      <div className="scroll gscroll">
        <table className="cov gap">
          <thead><tr><th>Experiment</th>{FIELDS.map(([k, l]) => <th key={k}>{l}</th>)}<th>Status</th></tr></thead>
          <tbody>
            {show.map((r) => (
              <tr key={r.id} className={sel === r.id ? "sel" : ""} onClick={() => setSel(r.id)}>
                <th>{r.name}{r.verify && <span className="vtag" title="Seed data says to verify this in PSI">verify</span>}</th>
                {FIELDS.map(([k, l]) => <Dot key={k} r={r} k={k} label={l} />)}
                <td className="gst"><span className={`gtag ${r.status}`}>{LABEL[r.status]}</span></td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
      {!show.length && <p className="dim note">Nothing in this view.</p>}
      <p className="dim note">
        <span className="gdot have" /> in the original record · <span className="gdot new" /> filled from a NASA source · <span className="gdot none" /> still unknown.
        Filled values come from the test conditions loaded into the API; click a row to see the source.
      </p>
    </Panel>
  );
}
