import json, pathlib
import reference, scoring

ROWS = json.loads((pathlib.Path(__file__).parents[1] / "data" / "seed.json").read_text())
ids = lambda out: [r["id"] for r in out]


def test_all_psi_investigations_present():
    need = {"bass", "bass-ii", "saffire-i", "saffire-ii", "saffire-iii", "same", "same-r", "daft", "daft-2", "flex", "flex-2",
            "cfi", "cfi-g", "bre", "e-field", "cld-flame", "s-flame", "flame-design", "spice", "slice",
            "cool-flame-cfd", "fgm-flame-spread", "spice-analysis", "cool-flame-extinction", "smoke-growth-sim"}
    assert need == set(ids(ROWS))
    assert all(r.get("psi_id", "").startswith("PSI-") for r in ROWS)


def test_default_rank_prefers_solid_flammability():
    out = scoring.filter_rank(ROWS, {})
    assert out[0]["id"] in ("bass", "bass-ii") and out[0]["score"] >= out[-1]["score"]


def test_focus_reorders():
    assert scoring.filter_rank(ROWS, {"focus": "detection"})[0]["id"] in ("same", "same-r")
    assert scoring.filter_rank(ROWS, {"focus": "suppression"})[0]["id"] in ("flex", "flex-2")


def test_filters():
    assert {r["fuel_type"] for r in scoring.filter_rank(ROWS, {"fuel": "gas"})} == {"gas"}
    assert ids(scoring.filter_rank(ROWS, {"o2_min": "30"})) == ["cfi-g", "flex-2"]
    assert "flex" in ids(scoring.filter_rank(ROWS, {"q": "diluent"}))
    assert {r["tier"] for r in scoring.filter_rank(ROWS, {"tier": "direct"})} == {"direct"}


def test_environments_and_partial_pressure():
    e = scoring.ENVIRONMENTS
    assert e["moon_base"]["pp_o2_psi"] == 3.06 and e["iss"]["pp_o2_psi"] == 3.09 and e["spacesuit"]["pp_o2_psi"] == 4.3
    assert set(e) == {"iss", "spacecraft", "moon_base", "rover", "mars_base", "spacesuit"}


def test_moon_base_scenario_reranks_and_filters():
    out = scoring.filter_rank(ROWS, {"scenario": "moon_base"})
    assert {"cfi-g", "bass-ii"} <= set(ids(out)) and not {"same", "bass"} & set(ids(out))
    assert [r["id"] for r in out if r["fits"]["moon_base"] == "confirmed"] == ["cfi-g", "flex-2"]
    base = next(r for r in scoring.filter_rank(ROWS, {}) if r["id"] == "cfi-g")["score"]
    assert next(r for r in out if r["id"] == "cfi-g")["score"] > base


def test_similar_and_compare():
    bass = next(r for r in ROWS if r["id"] == "bass")
    assert scoring.similar(ROWS, bass)[0]["id"] == "bass-ii"
    c = scoring.compare(ROWS, ["bass", "flex"])
    assert "Fuel type" in c["different_fields"] and "Gravity" in c["same_fields"]
    assert scoring.compare(ROWS, ["same", "same-r"])["shared_tags"] == ["aerosol", "detection", "smoke"]


def test_equipment_hardware_coverage():
    eq = scoring.equipment(ROWS, reference.CONTROL_AREAS)
    assert set(eq) == set(reference.CONTROL_AREAS) and eq["smoke_detection"]["investigations"][0]["id"] in ("same", "same-r")
    assert "flex" in [i["id"] for i in eq["suppression_systems"]["investigations"]]
    assert len(scoring.hardware_groups(ROWS)["ACME / CIR"]["investigations"]) == 6
    assert scoring.coverage(ROWS)["computed_gaps"]
