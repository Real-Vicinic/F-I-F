// Client-side ranking: six factors (0..1) per investigation, blended by the slider weights.
export const FACTORS = [
  { key: "relevance", label: "fire relevance", def: 0.25, tip: "Prevention, detection and suppression coverage, plus relevance tier" },
  { key: "evidence", label: "evidence", def: 0.2, tip: "Flight data beats ground data and models; recorded oxygen or pressure helps" },
  { key: "actionability", label: "actionability", def: 0.15, tip: "How many control areas it informs, and whether it has an Earth application" },
  { key: "atmosphere", label: "atmosphere fit", def: 0.1, tip: "Oxygen coverage for the selected environment (average of ISS, Moon, suit if none)" },
  { key: "richness", label: "data richness", def: 0.1, tip: "Sensors, oxygen, airflow and pressure recorded" },
  { key: "coverage", label: "variable coverage", def: 0.2, tip: "Number of variables varied across tests" },
];
export const DEFAULT_W = Object.fromEntries(FACTORS.map((f) => [f.key, f.def]));

const TIER = { direct: 1, related: 0.6, indirect: 0.3 };
const FIT = { confirmed: 1, possible: 0.6, unknown: 0.2, no: 0 };
const FOCUS = { all: [1, 1, 1], prevention: [3, 1, 1], detection: [1, 3, 1], suppression: [1, 1, 3] };
const arr = (v) => (Array.isArray(v) ? v : []);
const c1 = (n) => Math.max(0, Math.min(1, n));

export function factors(i, { focus = "all", scenario = "" } = {}) {
  const w = FOCUS[focus] || FOCUS.all;
  const fn = c1((w[0] * i.prevention + w[1] * i.detection + w[2] * i.suppression) / (2 * (w[0] + w[1] + w[2])));
  const tier = TIER[i.tier] ?? 0.3;
  const flight = /ISS|Cygnus/i.test(i.facility || "");
  const fits = i.fits || {};
  const fit = scenario ? FIT[fits[scenario]] ?? 0.2 : (FIT[fits.iss] + FIT[fits.moon_base] + FIT[fits.spacesuit]) / 3 || 0;
  return {
    relevance: c1(0.7 * fn + 0.3 * tier),
    evidence: c1((flight ? 0.55 : 0.15) + 0.25 * tier + (i.o2_max != null || i.pressure_psi != null ? 0.2 : 0)),
    actionability: c1(0.8 * Math.min(1, arr(i.informs).length / 3) + (i.earth_application ? 0.2 : 0)),
    atmosphere: c1(fit),
    richness: c1(0.4 * Math.min(1, arr(i.sensors).length / 3) + (i.o2_note ? 0.2 : 0) + (i.airflow ? 0.2 : 0) + (i.pressure_psi != null ? 0.2 : 0)),
    coverage: c1(arr(i.variables).length / 4),
  };
}

export function blend(fx, w) {
  const tot = FACTORS.reduce((s, f) => s + w[f.key], 0);
  return tot ? FACTORS.reduce((s, f) => s + w[f.key] * fx[f.key], 0) / tot : 0;
}

// Fire variable coverage: which variables each investigation records or varies (derived from its metadata).
const txt = (i) => [...arr(i.variables), ...arr(i.sensors), ...arr(i.tags), i.o2_note, i.airflow, i.objective].filter(Boolean).join(" | ");
const vars = (i) => [...arr(i.variables), ...arr(i.tags)].join(" | ");
const has = (re, s) => re.test(s);
export const COVER = [
  ["Fuel", "Fuel material", (i) => has(/fuel|material|sample|droplet|dust/i, vars(i))],
  ["Form", "Fuel form", (i) => has(/geometry|scale|size|droplet|dust|solid|liquid|gas|aerosol/i, vars(i))],
  ["Geom", "Fuel geometry", (i) => !!i.fuel_geometry && !/to verify/i.test(i.fuel_geometry)],
  ["O2", "Oxygen concentration", (i) => !!i.o2_note || has(/oxygen|o2/i, vars(i))],
  ["Dil", "Diluent gas", (i) => has(/diluent|nitrogen|dilution|atmosphere|helium|diluents/i, vars(i))],
  ["P", "Pressure", (i) => i.pressure_psi != null || has(/pressure|atmosphere/i, txt(i))],
  ["T0", "Ambient temperature", (i) => has(/ambient|thermal/i, vars(i))],
  ["Flow", "Flow regime", (i) => !!i.airflow || has(/flow/i, vars(i))],
  ["V", "Flow velocity", (i) => has(/velocity|speed|cm\/s/i, vars(i) + (i.airflow || ""))],
  ["g", "Gravity level", (i) => !!i.gravity],
  ["Ign", "Ignition source", (i) => has(/ignit/i, txt(i))],
  ["Shape", "Flame geometry", (i) => has(/shape|spher|geometry|flame_structure/i, vars(i))],
  ["Spread", "Flame spread rate", (i) => has(/spread/i, txt(i))],
  ["Tmax", "Peak temperature", (i) => has(/temperature|pyrometry/i, arr(i.sensors).join(" "))],
  ["Ext", "Extinction mode", (i) => has(/extinct|suppress/i, vars(i) + (i.objective || ""))],
  ["LOC", "Limiting oxygen", (i) => has(/o2_variation|high_o2|limiting oxygen/i, vars(i) + (i.objective || ""))],
  ["Prod", "Combustion products", (i) => has(/soot|smoke|particle|ion current|aerosol|dust/i, txt(i))],
];
