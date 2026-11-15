export const Score = ({ v }) => (
  <div className="score" title={`Relevance ${v}/100`}>
    <div className="track">
      <div className="fill" style={{ width: `${v}%`, backgroundSize: `${v > 0 ? 10000 / v : 100}% 100%` }} />
    </div>
    <span>{v}</span>
  </div>
);

export const FlameMark = () => (
  <svg viewBox="0 0 24 28" aria-hidden="true">
    <path d="M12 1C14 8 21 11 21 18.5 21 24 17 27 12 27S3 24 3 18.5C3 11 10 8 12 1Z" fill="#e4501b" />
    <path d="M12 12C13 16 16 17 16 20.5 16 23 14.3 24.5 12 24.5S8 23 8 20.5C8 17 11 16 12 12Z" fill="#ffd166" />
  </svg>
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
