// Data-gap analysis. "base" = what the investigation record already had;
// "now" = base plus any test-condition rows loaded from PSI/NASA sources (the /conditions endpoint).
export const FIELDS = [
  ["o2", "O₂", (i) => i.o2_min != null || i.o2_max != null, (c) => c.o2_pct != null],
  ["pressure", "Pressure", (i) => i.pressure_psi != null, (c) => c.pressure_psi != null],
  ["airflow", "Airflow", (i) => !!i.airflow, (c) => c.airflow_cm_s != null],
];

export function analyze(items, conds) {
  const rows = (items || []).map((i) => {
    const cs = conds.filter((c) => c.investigation_id === i.id);
    const base = {}, now = {};
    FIELDS.forEach(([k, , fromInv, fromCond]) => { base[k] = fromInv(i); now[k] = base[k] || cs.some(fromCond); });
    const filled = FIELDS.map(([k]) => k).filter((k) => now[k] && !base[k]);
    const open = FIELDS.map(([k]) => k).filter((k) => !now[k]);
    const verify = /verify/i.test([i.o2_note, i.fuel_geometry, i.fuels].join(" "));
    return { id: i.id, name: i.name, base, now, filled, open, verify, rows: cs,
      status: filled.length ? (open.length ? "partial" : "updated") : open.length ? "open" : "complete" };
  });
  const totals = Object.fromEntries(FIELDS.map(([k]) => [k, {
    base: rows.filter((r) => r.base[k]).length, now: rows.filter((r) => r.now[k]).length, total: rows.length }]));
  return {
    rows, totals,
    updated: rows.filter((r) => r.filled.length).length,
    withOpen: rows.filter((r) => r.open.length).length,
  };
}
