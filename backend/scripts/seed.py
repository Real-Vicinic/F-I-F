import json, os, pathlib, sys, psycopg
from psycopg.types.json import Jsonb

ROOT = pathlib.Path(__file__).parents[1]
sys.path.insert(0, str(ROOT / "src"))
import reference, scoring

COLS = ["name", "full_name", "family", "hardware_family", "hardware", "facility", "fuel_type", "fuels", "fuel_geometry", "objective",
        "tier", "informs", "o2_min", "o2_max", "o2_note", "pressure_psi", "airflow", "gravity", "tags", "prevention", "detection",
        "suppression", "earth_application", "source_url", "safety_relevance_score", "psi_id"]
UPSERT = (f"INSERT INTO investigations (id,{','.join(COLS)}) VALUES (%s,{','.join(['%s'] * len(COLS))}) "
          f"ON CONFLICT (id) DO UPDATE SET {','.join(f'{c}=EXCLUDED.{c}' for c in COLS)}")


def inv_chunks(r):
    n = r["name"]
    return [
        ("objective", f"{n} ({r['full_name']}{', ' + r['psi_id'] if r.get('psi_id') else ''}): {r['objective']}"),
        ("conditions", f"{n} test conditions: fuel type {r['fuel_type']}; fuels: {r['fuels']}; sample or burner geometry: {r['fuel_geometry'] or 'not specified'}; "
                       f"hardware: {r['hardware']} on {r['facility']}; O2 (oxygen) concentration: {r['o2_note'] or 'not specified'}; "
                       f"airflow: {r['airflow'] or 'not specified'}; gravity: {r['gravity']}."),
        ("safety", f"{n} fire-safety relevance ({r['tier']}): prevention {r['prevention']}/3, detection {r['detection']}/3, suppression {r['suppression']}/3; "
                   f"informs: {', '.join(r['informs'])}; tags: {', '.join(r['tags'])}."
                   + (" Tested at or above the 30% oxygen expected in a Moon Base." if (r["o2_max"] or 0) >= 30 else "")
                   + (f" Earth application: {r['earth_application']}" if r["earth_application"] else "")),
        ("measurements", f"{n} variables varied: {', '.join(r['variables'])}; sensors: {', '.join(r['sensors'])}."),
    ]


def ref_chunks(rows):
    names = {r["id"]: r["name"] for r in rows}
    out = []
    for e in scoring.ENVIRONMENTS.values():
        pp = f" O2 partial pressure {e['pp_o2_psi']} psia." if e["pp_o2_psi"] else ""
        o2 = f"{e['o2_pct']}% O2 at {e['psi']} psi." if e["o2_pct"] else "Atmosphere not specified."
        out.append(f"Environment {e['label']}: {o2}{pp} {e['note']}")
    for x in reference.EARTH:
        out.append(f"Earth application, {x['title']}: {x['origin']}; {x['earth_use']}. Related: {', '.join(names.get(i, i) for i in x['related']) or 'none'}.")
    for g in reference.GAPS:
        out.append(f"Data gap, {g['title']}: {g['detail']}")
    for a, d in reference.CONTROL_AREAS.items():
        m = [r["name"] for r in rows if a in r["informs"]]
        out.append(f"Fire-safety control area {a.replace('_', ' ')}: {d} Informed by: {', '.join(m)}.")
    return out


data = json.loads((ROOT / "data" / "seed.json").read_text())
with psycopg.connect(os.environ["DATABASE_URL"]) as c:
    for r in data:
        r["safety_relevance_score"] = scoring.score(r)
        c.execute(UPSERT, [r["id"]] + [r.get(k) for k in COLS])
        c.execute("INSERT INTO experiments (investigation_id,variables_json,sensors_json) VALUES (%s,%s,%s) "
                  "ON CONFLICT (investigation_id) DO UPDATE SET variables_json=EXCLUDED.variables_json, sensors_json=EXCLUDED.sensors_json",
                  (r["id"], Jsonb(r["variables"]), Jsonb(r["sensors"])))
        c.execute("DELETE FROM chunks WHERE investigation_id=%s", (r["id"],))
        for kind, text in inv_chunks(r):
            c.execute("INSERT INTO chunks (investigation_id,kind,text) VALUES (%s,%s,%s)", (r["id"], kind, text))
        c.execute("DELETE FROM test_conditions WHERE investigation_id=%s AND source='seed'", (r["id"],))
        for t in r["conditions"]:
            c.execute("INSERT INTO test_conditions (investigation_id,o2_pct,pressure_psi,airflow_cm_s,note,source) VALUES (%s,%s,%s,%s,%s,'seed')",
                      (r["id"], t.get("o2_pct"), t.get("pressure_psi"), t.get("airflow_cm_s"), t.get("note")))
    c.execute("DELETE FROM chunks WHERE investigation_id IS NULL")
    for text in ref_chunks(data):
        c.execute("INSERT INTO chunks (investigation_id,kind,text) VALUES (NULL,'reference',%s)", (text,))
print(f"seeded {len(data)} investigations")
