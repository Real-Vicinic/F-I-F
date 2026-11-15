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
    {"id": "mist-extinguisher", "title": "Water-mist portable extinguishers", "origin": "Certified for spaceflight after years of research; the first two of nine units reached the ISS in December 2015 to replace CO2 units",
     "earth_use": "Non-toxic replacement for banned Halon systems", "related": ["flex", "flex-2"]},
    {"id": "particle-fire-detector", "title": "Particulate-and-species fire detector", "origin": "Device from NASA Glenn microgravity fire research that monitors particles and chemical species together",
     "earth_use": "In joint FAA testing it beat current aircraft smoke detectors on false-alarm rejection and real-event detection", "related": ["same", "same-r", "daft"]},
    {"id": "low-swirl-burner", "title": "Ultra-low-emission burner", "origin": "Burner invented in microgravity premixed-flame work (NASA, Lawrence Berkeley Lab Ultraclean Low Swirl project)",
     "earth_use": "Applications in domestic water heaters and furnaces", "related": []},
    {"id": "smoke-detector", "title": "Shuttle-derived smoke detector", "origin": "1970s detector that discriminates smoke from dust",
     "earth_use": "Fewer nuisance alarms; industrial uses such as mining", "related": ["same", "same-r", "daft", "daft-2"]},
    {"id": "air-tanks", "title": "Firefighter air tanks", "origin": "1970s adaptation of spacesuit technology",
     "earth_use": "Improved firefighter breathing gear", "related": []},
    {"id": "fire-attire", "title": "Firefighter protective clothing", "origin": "1980s application of NASA spacesuit technology",
     "earth_use": "Improved protective clothing", "related": []},
]

MISCONCEPTIONS = [
    "A steady fire cannot exist in a quiescent microgravity environment.",
    "A fire will self-extinguish if ventilation is shut off.",
    "Reduced gravity is inherently safer, so terrestrial fire standards and tests are very conservative.",
]
FIRE_TRIANGLE_NOTE = ("Crewed spacecraft contain fuel, oxygen and ignition sources, often at a higher oxygen fraction than air, "
                      "with limited escape options and little tolerance for damage to life support.")

INCIDENTS = [
    {"id": "apollo-1", "title": "Apollo 1", "year": 1967,
     "summary": "A cabin fire broke out during a launch-pad test and killed three NASA astronauts. An investigation followed and lessons were learned."},
    {"id": "apollo-13", "title": "Apollo 13", "year": 1970,
     "summary": "An oxygen tank exploded during the flight to the Moon. An investigation followed and lessons were learned."},
    {"id": "mir-fire", "title": "Fire aboard Mir", "year": 1997,
     "summary": "A fire caused by an oxygen generator failure erupted on the Russian space station Mir during joint operations preparing for the ISS."},
]

RESOURCES = [
    {"title": "A Researcher's Guide to: Combustion Science (NASA ISS Program Science Office, 2015)",
     "detail": "Source for fuels, hardware and oxygen ranges added to the investigations.",
     "url": "https://www.nasa.gov/sites/default/files/atoms/files/np-2015-10-034-jsc_combustion_in_reduced_gravity-iss-mini-book-011116-508.pdf"},
    {"title": "NASA ScienceCasts: The Power of Studying Combustion on the ISS",
     "detail": "3.6-minute introduction to NASA combustion research on the ISS (2018).",
     "url": "https://www.issnationallab.org/blog/nasa-sciencecasts-the-power-of-studying-combustion-on-the-iss/"},
    {"title": "Challenge resources: Flame in Freefall",
     "detail": "NASA Space Apps Challenge resource list for this challenge.",
     "url": "https://www.spaceappschallenge.org/2026/challenges/flame-in-freefall/?tab=resources"},
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
        "scope_note": "Curated from NASA PSI summaries and the 2015 ISS Combustion Science Researcher's Guide. Verify values in PSI before use."}
