"""Load per-test conditions downloaded from NASA PSI. Safe to re-run: identical rows are skipped.
CSV columns: investigation_id,o2_pct,pressure_psi,airflow_cm_s,note  (blank = unknown)
Usage: python scripts/import_conditions.py conditions.csv
"""
import csv, os, sys, psycopg

num = lambda v: float(v) if v not in (None, "") else None

SQL = """
INSERT INTO test_conditions (investigation_id,o2_pct,pressure_psi,airflow_cm_s,note,source)
SELECT %(i)s, %(o)s::real, %(p)s::real, %(a)s::real, %(n)s, 'import'
WHERE NOT EXISTS (
  SELECT 1 FROM test_conditions
  WHERE investigation_id = %(i)s
    AND o2_pct IS NOT DISTINCT FROM %(o)s::real
    AND pressure_psi IS NOT DISTINCT FROM %(p)s::real
    AND airflow_cm_s IS NOT DISTINCT FROM %(a)s::real
    AND note IS NOT DISTINCT FROM %(n)s
)"""

added = dup = unknown = 0
with psycopg.connect(os.environ["DATABASE_URL"]) as c, open(sys.argv[1], newline="", encoding="utf-8") as f:
    known = {r[0] for r in c.execute("SELECT id FROM investigations")}
    for r in csv.DictReader(f):
        iid = (r.get("investigation_id") or "").strip()
        if iid not in known:
            print(f"skip unknown investigation_id: {iid!r}")
            unknown += 1
            continue
        cur = c.execute(SQL, {"i": iid, "o": num(r.get("o2_pct")), "p": num(r.get("pressure_psi")),
                              "a": num(r.get("airflow_cm_s")), "n": (r.get("note") or "").strip() or None})
        if cur.rowcount:
            added += 1
        else:
            dup += 1
print(f"added {added}, duplicates skipped {dup}, unknown ids skipped {unknown}")
