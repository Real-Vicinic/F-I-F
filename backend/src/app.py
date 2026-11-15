import csv, io, json, os, re
import db, rag, reference, scoring

CORS = {"Access-Control-Allow-Origin": os.environ.get("ALLOWED_ORIGIN", "*"),
        "Access-Control-Allow-Headers": "Content-Type", "Access-Control-Allow-Methods": "GET,POST,OPTIONS"}
EXPORT = ["id", "name", "psi_id", "full_name", "family", "tier", "fuel_type", "fuels", "fuel_geometry", "hardware", "facility", "o2_min", "o2_max",
          "o2_note", "pressure_psi", "airflow", "gravity", "variables", "sensors", "tags", "informs", "prevention", "detection",
          "suppression", "score", "source_url"]


def resp(code, body, ctype="application/json", extra=None):
    payload = body if isinstance(body, str) else json.dumps(body, default=str)
    return {"statusCode": code, "headers": {**CORS, "Content-Type": ctype, **(extra or {})}, "body": payload}


def to_csv(rows, cols):
    buf = io.StringIO()
    w = csv.writer(buf)
    w.writerow(cols)
    for r in rows:
        w.writerow(["; ".join(map(str, v)) if isinstance(v, (list, tuple)) else ("" if v is None else v) for v in (r.get(c) for c in cols)])
    return buf.getvalue()


def export(qs):
    fmt = qs.get("format", "csv")
    if fmt not in ("csv", "json"):
        raise ValueError("format must be csv or json")
    kind = qs.get("kind", "investigations")
    if kind == "conditions":
        rows, cols = db.conditions(qs.get("investigation_id")), ["investigation_id", "o2_pct", "pressure_psi", "airflow_cm_s", "note", "source"]
    elif kind == "investigations":
        rows, cols = scoring.filter_rank(db.investigations(), qs), EXPORT
    else:
        raise ValueError("kind must be investigations or conditions")
    if fmt == "json":
        return resp(200, [{c: r.get(c) for c in cols} for r in rows])
    return resp(200, to_csv(rows, cols), "text/csv", {"Content-Disposition": f'attachment; filename="flame-{kind}.csv"'})


def handler(event, _ctx):
    m, path = event["httpMethod"], event["path"].rstrip("/") or "/"
    qs = event.get("queryStringParameters") or {}
    try:
        if m == "OPTIONS":
            return {"statusCode": 204, "headers": CORS, "body": ""}
        if path == "/health":
            return resp(200, {"ok": True})
        if path in ("/environments", "/scenarios"):
            return resp(200, scoring.ENVIRONMENTS)
        if path == "/meta":
            return resp(200, {**reference.META, "control_areas": reference.CONTROL_AREAS, "gaps": reference.GAPS,
                              "incidents": reference.INCIDENTS, "resources": reference.RESOURCES})
        if path == "/earth":
            rows = {r["id"]: r for r in db.investigations()}
            items = [{**x, "related": [{"id": i, "name": rows[i]["name"]} for i in x["related"] if i in rows]} for x in reference.EARTH]
            return resp(200, {"items": items, "from_investigations": [
                {"id": r["id"], "name": r["name"], "earth_application": r["earth_application"]} for r in rows.values() if r.get("earth_application")]})
        if path == "/equipment":
            return resp(200, scoring.equipment(db.investigations(), reference.CONTROL_AREAS))
        if path == "/hardware":
            return resp(200, scoring.hardware_groups(db.investigations()))
        if path == "/coverage":
            return resp(200, {**scoring.coverage(db.investigations()), "static_gaps": reference.GAPS})
        if path == "/compare":
            ids = [i for i in (qs.get("ids") or "").split(",") if i]
            if not 2 <= len(ids) <= 4:
                raise ValueError("ids must list 2 to 4 investigation ids")
            return resp(200, scoring.compare(db.investigations(), ids))
        if path == "/export":
            return export(qs)
        if path == "/conditions":
            return resp(200, {"items": db.conditions(qs.get("investigation_id"))})
        if path == "/investigations" and m == "GET":
            rows = scoring.filter_rank(db.investigations(), qs)
            lim, off = min(int(qs.get("limit", 50)), 100), int(qs.get("offset", 0))
            return resp(200, {"total": len(rows), "items": rows[off:off + lim]})
        mt = re.fullmatch(r"/investigations/([\w-]+)", path)
        if mt and m == "GET":
            rows = db.investigations()
            inv = next((r for r in rows if r["id"] == mt.group(1)), None)
            if not inv:
                return resp(404, {"error": "not found"})
            full = scoring.filter_rank([inv], {})[0]
            return resp(200, {**full, "similar": scoring.similar(rows, inv), "conditions": db.conditions(inv["id"]),
                              "same": {k: inv.get(k) for k in ("hardware", "facility", "gravity")}, "varied": inv.get("variables")})
        if path == "/search" and m == "GET":
            hits = {}
            for c in rag.retrieve(qs.get("q", "")):
                hits.setdefault(c["id"] or c["name"], {"id": c["id"], "name": c["name"], "snippet": c["text"]})
            return resp(200, {"items": list(hits.values())})
        if path == "/chat" and m == "POST":
            body = json.loads(event.get("body") or "{}")
            if not body.get("question"):
                return resp(400, {"error": "question required"})
            return resp(200, rag.ask(body["question"], body.get("investigation_id")))
        return resp(404, {"error": "not found"})
    except (ValueError, KeyError) as e:
        return resp(400, {"error": str(e)})
    except Exception as e:
        print("error", repr(e))
        return resp(500, {"error": "internal error"})
