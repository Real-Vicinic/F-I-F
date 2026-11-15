import "./FlameStage.css";

/**
 * Animated Earth vs microgravity flames.
 * Drop it inside the "Ask the data" card, between the input row and the answer.
 * The input and the Ask button are not touched.
 *
 * Props:
 *   busy    - true while the assistant is answering; the flames burn faster.
 *   compact - smaller flames without captions, for when messages fill the chat.
 */
export default function FlameStage({ busy = false, compact = false }) {
  return (
    <div className={`flame-stage${busy ? " is-busy" : ""}${compact ? " is-compact" : ""}`}>
      <figure className="flame-fig">
        <svg viewBox="0 0 120 140" aria-hidden="true">
          <defs>
            <path
              id="fs-drop"
              d="M60 6 C70 38 96 60 96 92 C96 118 80 132 60 132 C40 132 24 118 24 92 C24 60 50 38 60 6 Z"
            />
            <linearGradient id="fs-outer" x1="0" y1="1" x2="0" y2="0">
              <stop offset="0" stopColor="#e8590c" />
              <stop offset="1" stopColor="#ff9a3d" />
            </linearGradient>
            <linearGradient id="fs-mid" x1="0" y1="1" x2="0" y2="0">
              <stop offset="0" stopColor="#ff8a1f" />
              <stop offset="1" stopColor="#ffc15e" />
            </linearGradient>
            <linearGradient id="fs-core" x1="0" y1="1" x2="0" y2="0">
              <stop offset="0" stopColor="#ffc94d" />
              <stop offset="1" stopColor="#fff1b8" />
            </linearGradient>
            <filter id="fs-soft" x="-30%" y="-30%" width="160%" height="160%">
              <feGaussianBlur stdDeviation="4" />
            </filter>
          </defs>

          <ellipse className="fs-earth-glow" cx="60" cy="100" rx="40" ry="30" fill="#ff7a1a" filter="url(#fs-soft)" />
          <g className="fs-flick fs-a">
            <use href="#fs-drop" fill="url(#fs-outer)" />
          </g>
          <g transform="translate(60 132) scale(.7) translate(-60 -132)">
            <g className="fs-flick fs-b">
              <use href="#fs-drop" fill="url(#fs-mid)" />
            </g>
          </g>
          <g transform="translate(60 132) scale(.4) translate(-60 -132)">
            <g className="fs-flick fs-c">
              <use href="#fs-drop" fill="url(#fs-core)" />
            </g>
          </g>
        </svg>
        <figcaption>Earth: buoyant, elongated</figcaption>
      </figure>

      <figure className="flame-fig">
        <svg viewBox="0 0 120 140" aria-hidden="true">
          <circle className="fs-halo" cx="60" cy="70" r="30" fill="none" stroke="#ff9a3d" strokeWidth="2" />
          <circle className="fs-micro-glow" cx="60" cy="70" r="44" fill="#ff7a1a" filter="url(#fs-soft)" />
          <circle className="fs-breathe fs-d" cx="60" cy="70" r="34" fill="none" stroke="#ff8a1f" strokeWidth="5" />
          <circle className="fs-breathe fs-e" cx="60" cy="70" r="26" fill="#ff7a1a" />
          <circle className="fs-breathe fs-f" cx="60" cy="70" r="14" fill="#ffd166" />
        </svg>
        <figcaption>Microgravity: spherical, diffusion-driven</figcaption>
      </figure>
    </div>
  );
}
