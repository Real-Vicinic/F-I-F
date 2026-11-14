"""Load per-test conditions downloaded from NASA PSI.
CSV columns: investigation_id,o2_pct,pressure_psi,airflow_cm_s,note  (blank = unknown)
Usage: python scripts/import_conditions.py conditions.csv
"""
import csv, os, sys, psycopg

num = lambda v: float(v) if v not in (None, "") else None
with psycopg.connect(os.environ["DATABASE_URL"]) as c, open(sys.argv[1], newline="", encoding="utf-8") as f:
    n = 0
    for r in csv.DictReader(f):
        c.execute("INSERT INTO test_conditions (investigation_id,o2_pct,pressure_psi,airflow_cm_s,note,source) VALUES (%s,%s,%s,%s,%s,'import')",
                  (r["investigation_id"], num(r.get("o2_pct")), num(r.get("pressure_psi")), num(r.get("airflow_cm_s")), r.get("note") or None))
        n += 1
print(f"imported {n} rows")
