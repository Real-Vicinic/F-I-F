export const Score = ({ v }) => (
  <div className="score" title={`Relevance ${v}/100`}>
    <div style={{ width: `${v}%` }} />
    <span>{v}</span>
  </div>
);

const FIT = { confirmed: "✓", possible: "~", no: "✗", unknown: "?" };
const NAMES = { iss: "ISS", moon_base: "Moon", spacesuit: "Suit" };

export const Fits = ({ fits }) => (
  <div className="fits">
    {Object.keys(NAMES).map((k) => (
      <span key={k} className={`fit ${fits[k]}`} title={`${k}: ${fits[k]}`}>{NAMES[k]} {FIT[fits[k]]}</span>
    ))}
  </div>
);

export const Tags = ({ tags = [] }) => (
  <div className="tags">{tags.map((t) => <span key={t}>{t}</span>)}</div>
);

export const State = ({ err, loading }) =>
  err ? <p className="err">Could not load data ({err}). Is the API running?</p> : loading ? <p className="dim">Loading…</p> : null;
