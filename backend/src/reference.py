PSI_URL = "https://psi.nasa.gov/"

CONTROL_AREAS = {
    "material_selection": "Prevention: choose materials using flammability limits as a function of oxygen concentration and airflow.",
    "atmosphere_limits": "Habitat atmosphere design: how oxygen enrichment (30% or more expected for a Moon Base) raises flammability.",
    "smoke_detection": "Detection: smoke sensing that works in microgravity and avoids dust-triggered nuisance alarms.",
    "suppression_systems": "Suppression: extinguishing agents and atmosphere dilution (CO2, helium) in microgravity.",
    "fire_modeling": "Predictive modeling of flammability and fire scenarios; validation data for simulations.",
}

EARTH = [
    {"id": "water-mist", "title": "Fine water-mist extinguishers", "origin": "Developed for use on the ISS",
     "earth_use": "Practical terrestrial fire suppression", "related": ["flex", "flex-2"]},
    {"id": "smoke-detector", "title": "Shuttle-derived smoke detector", "origin": "1970s detector that discriminates smoke from dust",
     "earth_use": "Fewer nuisance alarms; industrial uses such as mining", "related": ["same", "same-r", "daft", "daft-2"]},
    {"id": "air-tanks", "title": "Firefighter air tanks", "origin": "1970s adaptation of spacesuit technology",
     "earth_use": "Improved firefighter breathing gear", "related": []},
    {"id": "fire-attire", "title": "Firefighter protective clothing", "origin": "1980s application of NASA spacesuit technology",
     "earth_use": "Improved protective clothing", "related": []},
]

GAPS = [
    {"id": "partial-gravity", "title": "No partial-gravity data in PSI",
     "detail": "LUCI and FM2 are expected to add Moon-gravity data. E-FIELD Flames mimics partial gravity with electric fields in the meantime.",
     "related": ["e-field"]},
    {"id": "solid-high-o2", "title": "Solid-material data at Moon Base conditions not captured",
     "detail": "The highest-oxygen tests (CFI-G, up to 85%) burn gaseous fuels. Solid-material oxygen ranges are not captured in this curated seed; verify in PSI.",
     "related": ["cfi-g", "bass", "bass-ii"]},
    {"id": "rockets", "title": "Rocket and propellant fire safety out of scope",
     "detail": "High velocities in rocket engines make combustion effectively gravity-independent, so PSI does not cover it.", "related": []},
    {"id": "conditions", "title": "Per-test conditions not yet loaded",
     "detail": "Load PSI test conditions with scripts/import_conditions.py to enable richer modeling exports.", "related": []},
]

META = {"psi_url": PSI_URL,
        "audience": ["Professors", "Graduate students", "Undergraduate students", "Aerospace researchers", "Aerospace engineers"],
        "scope_note": "Curated summaries of NASA PSI combustion investigations. Verify values in PSI before use."}
