import json

ENVIRONMENTS = {
    "iss": {"label": "Space station (ISS-like)", "o2_pct": 21, "psi": 14.7, "fit_o2": 21, "basis": "brief",
            "note": "Earth-like cabin atmosphere."},
    "spacecraft": {"label": "Crewed spacecraft", "o2_pct": None, "psi": None, "fit_o2": 21, "basis": "assumed",
                   "note": "Cabin atmosphere not given in the challenge brief; treated like ISS for fit."},
    "moon_base": {"label": "Moon Base", "o2_pct": 30, "psi": 10.2, "fit_o2": 30, "basis": "brief",
                  "note": "Intermediate atmosphere: 30% O2 or more at 10.2 psi or less. 30% is over 40% more oxygen than Earth air, making materials much more flammable."},
    "rover": {"label": "Pressurized rover", "o2_pct": 30, "psi": 10.2, "fit_o2": 30, "basis": "brief",
              "note": "Expected to share the Moon Base intermediate atmosphere."},
    "mars_base": {"label": "Mars base", "o2_pct": None, "psi": None, "fit_o2": 30, "basis": "assumed",
                  "note": "Mars values are not in the brief; assumed to follow the Moon Base intermediate-atmosphere logic."},
    "spacesuit": {"label": "Spacesuit", "o2_pct": 100, "psi": 4.3, "fit_o2": 50, "basis": "brief",
                  "note": "No PSI test reaches 100% O2; high-oxygen data (CFI-G, up to 85%) is the closest bound."},
}
for _e in ENVIRONMENTS.values():
    _e["pp_o2_psi"] = round(_e["o2_pct"] * _e["psi"] / 100, 2) if _e["o2_pct"] and _e["psi"] else None
SCENARIOS = ENVIRONMENTS

_MOON = {"high_o2": 8, "o2_variation": 5, "material_flammability": 3}
ENV_BOOST = {
    "iss": {"smoke": 4, "aerosol": 2, "spacecraft_scale": 2},
    "spacecraft": {"spacecraft_scale": 8, "smoke": 4, "solid": 2},
    "moon_base": _MOON,
    "rover": {**_MOON, "smoke": 2},
    "mars_base": {**_MOON, "partial_g_analog": 3},
    "spacesuit": {"high_o2": 10, "o2_variation": 3},
}
FOCUS = {"all": (1, 1, 1), "prevention": (3, 1, 1), "detection": (1, 3, 1), "suppression": (1, 1, 3)}
FUNCS = ("prevention", "detection", "suppression")
BONUS = {"o2_variation": 4, "high_o2": 6, "flow_variation": 2, "spacecraft_scale": 4, "material_flammability": 3, "solid": 2}


def score(inv, focus="all", env=None):
    w = FOCUS.get(focus, FOCUS["all"])
    tags = inv.get("tags") or []
    raw = 10 * sum(w[i] * inv[f] for i, f in enumerate(FUNCS)) + sum(BONUS.get(t, 0) for t in tags) \
        + sum(ENV_BOOST.get(env, {}).get(t, 0) for t in tags)
    return min(100, round(raw / 0.75))


def scenario_fit(inv, key):
    o2, tags = inv.get("o2_max"), inv.get("tags") or []
    if o2 is not None:
        return "confirmed" if o2 >= ENVIRONMENTS[key]["fit_o2"] else "no"
    if key in ("iss", "spacecraft"):
        return "possible"
    if key in ("moon_base", "rover", "mars_base"):
        return "possible" if "o2_variation" in tags else "unknown"
    return "unknown"


def filter_rank(rows, p):
    focus, sc = p.get("focus", "all"), p.get("scenario")
    env = sc if sc in ENVIRONMENTS else None
    out = []
    for r in rows:
        if p.get("fuel") and r["fuel_type"] != p["fuel"]:
            continue
        if p.get("hardware") and p["hardware"].lower() not in ((r.get("hardware") or "") + " " + (r.get("hardware_family") or "")).lower():
            continue
        if p.get("family") and p["family"].lower() != (r.get("family") or "").lower():
            continue
        if p.get("tier") and p["tier"] != r.get("tier"):
            continue
        if p.get("tag") and p["tag"] not in (r.get("tags") or []):
            continue
        if p.get("o2_min") and (r.get("o2_max") is None or r["o2_max"] < float(p["o2_min"])):
            continue
        fits = {k: scenario_fit(r, k) for k in ENVIRONMENTS}
        if env and fits[env] not in ("confirmed", "possible"):
            continue
        if p.get("q"):
            blob = " ".join(str(r.get(k) or "") for k in ("name", "full_name", "family", "fuels", "fuel_geometry", "objective", "hardware", "tags")).lower()
            if not all(t in blob for t in p["q"].lower().split()):
                continue
        out.append({**r, "score": score(r, focus, env), "fits": fits})
    return sorted(out, key=lambda x: (-x["score"], x["name"]))


def similar(rows, inv, n=4):
    ranked = []
    for r in rows:
        if r["id"] == inv["id"]:
            continue
        s = 3 * (r.get("family") == inv.get("family")) + 2 * (r.get("hardware_family") == inv.get("hardware_family")) \
            + len(set(r.get("tags") or []) & set(inv.get("tags") or []))
        if s >= 2:
            ranked.append((s, r))
    ranked.sort(key=lambda x: (-x[0], x[1]["name"]))
    return [{"id": r["id"], "name": r["name"], "score": score(r)} for _, r in ranked[:n]]


CMP = [("tier", "Relevance tier"), ("fuel_type", "Fuel type"), ("fuels", "Fuels"), ("fuel_geometry", "Sample / burner geometry"),
       ("hardware", "Hardware"), ("facility", "Facility"), ("o2_note", "Oxygen"), ("airflow", "Airflow"), ("gravity", "Gravity"),
       ("variables", "Variables varied"), ("sensors", "Sensors"), ("informs", "Informs"),
       ("prevention", "Prevention (0-3)"), ("detection", "Detection (0-3)"), ("suppression", "Suppression (0-3)")]


def compare(rows, ids):
    by = {r["id"]: r for r in rows}
    sel = [by[i] for i in ids]
    fields = []
    for k, label in CMP:
        vals = {r["id"]: r.get(k) for r in sel}
        fields.append({"field": k, "label": label, "values": vals, "same": len({json.dumps(v) for v in vals.values()}) == 1})
    tagsets = [set(r.get("tags") or []) for r in sel]
    shared = sorted(set.intersection(*tagsets))
    return {"investigations": [{"id": r["id"], "name": r["name"], "score": score(r)} for r in sel], "fields": fields,
            "shared_tags": shared,
            "unique_tags": {r["id"]: sorted(t - set.union(*(o for o in tagsets if o is not t)) if len(tagsets) > 1 else t) for r, t in zip(sel, tagsets)},
            "same_fields": [f["label"] for f in fields if f["same"]], "different_fields": [f["label"] for f in fields if not f["same"]]}


def equipment(rows, areas):
    out = {}
    for a, desc in areas.items():
        m = sorted((r for r in rows if a in (r.get("informs") or [])), key=lambda r: (-score(r), r["name"]))
        out[a] = {"description": desc, "investigations": [{"id": r["id"], "name": r["name"], "score": score(r), "tier": r.get("tier")} for r in m]}
    return out


def hardware_groups(rows):
    g = {}
    for r in rows:
        k = r.get("hardware_family") or "Other"
        g.setdefault(k, {"hardware": r.get("hardware"), "investigations": []})["investigations"].append({"id": r["id"], "name": r["name"]})
    return g


def coverage(rows):
    envs, gaps = {}, []
    for env, e in ENVIRONMENTS.items():
        fit = {r["id"]: scenario_fit(r, env) for r in rows}
        ok = [r for r in rows if fit[r["id"]] in ("confirmed", "possible")]
        by_f = {}
        for f in FUNCS:
            m = sorted((r for r in ok if r[f] > 0), key=lambda r: (-r[f], -score(r, "all", env), r["name"]))
            by_f[f] = [{"id": r["id"], "name": r["name"], "fit": fit[r["id"]]} for r in m]
            if not m:
                gaps.append(f"No investigation with confirmed or possible oxygen coverage addresses {f} for {e['label']}.")
        envs[env] = {"label": e["label"], "confirmed": [i for i, v in fit.items() if v == "confirmed"],
                     "possible": [i for i, v in fit.items() if v == "possible"], "by_function": by_f}
    return {"environments": envs, "computed_gaps": gaps}
