PSI_URL = "https://psi.nasa.gov/"
NASA = "https://www.nasa.gov/"
APOLLO1 = NASA + "wp-content/uploads/static/history/"

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
    {"id": "smoke-detector", "url": "https://spinoff.nasa.gov/node/9407", "title": "Shuttle-derived smoke detector", "origin": "1970s detector that discriminates smoke from dust",
     "earth_use": "Fewer nuisance alarms; industrial uses such as mining", "related": ["same", "same-r", "daft", "daft-2"]},
    {"id": "air-tanks", "url": "https://spinoff.nasa.gov/node/9582", "title": "Firefighter air tanks", "origin": "1970s adaptation of spacesuit technology",
     "earth_use": "Improved firefighter breathing gear", "related": []},
    {"id": "fire-attire", "url": "https://spinoff.nasa.gov/node/9918", "title": "Firefighter protective clothing", "origin": "1980s application of NASA spacesuit technology",
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
    {"id": "apollo-1", "url": "https://www.nasa.gov/history/apollo-1/", "title": "Apollo 1", "year": 1967,
     "summary": "A fire in a 100% oxygen cabin during a launch-pad test killed three NASA astronauts. The Review Board found the fire spread in three stages along nylon netting and Velcro, and the cabin ruptured about 15 seconds after the fire call. Lessons: restrict combustible materials, add a water-based extinguisher, treat 100% oxygen tests as hazardous."},
    {"id": "apollo-13", "url": "https://www.nasa.gov/history/apollo-13-mission-details/", "title": "Apollo 13", "year": 1970,
     "summary": "An oxygen tank exploded during the flight to the Moon. An investigation followed and lessons were learned."},
    {"id": "mir-fire", "url": "https://www.nasa.gov/history/25-years-ago-fire-aboard-space-station-mir/", "title": "Fire aboard Mir", "year": 1997,
     "summary": "A fire caused by an oxygen generator failure erupted on the Russian space station Mir during joint operations preparing for the ISS."},
]

RESOURCES = [
    # --- NASA Space Apps challenge resource list ---
    {"group": "Challenge resources", "title": "PSI Data Repository: Combustion Science",
     "detail": "Physical Sciences Informatics source of the data this app is based on.",
     "url": "https://psi.nasa.gov/physci/repo/search?q=combustion&data_source=psi&data_type=investigation"},
    {"group": "Challenge resources", "title": "NASA Combustion Science",
     "detail": "NASA Glenn overview of combustion research on the ISS.",
     "url": "https://www.nasa.gov/glenn/glenn-expertise-space-exploration/physical-sciences-program/combustion-science"},
    {"group": "Challenge resources", "title": "NASA ScienceCasts: The Power of Studying Combustion on the ISS",
     "detail": "3.6-minute introduction to NASA combustion research on the ISS (2018).",
     "url": "https://www.issnationallab.org/blog/nasa-sciencecasts-the-power-of-studying-combustion-on-the-iss/"},
    {"group": "Challenge resources", "title": "A Researcher's Guide to: Combustion Science (NASA ISS Program Science Office, 2015)",
     "detail": "Source for fuels, hardware and oxygen ranges added to the investigations.",
     "url": "https://www.nasa.gov/sites/default/files/atoms/files/np-2015-10-034-jsc_combustion_in_reduced_gravity-iss-mini-book-011116-508.pdf"},
    {"group": "Challenge resources", "title": "Apollo 1",
     "detail": "Cabin fire during a launch-pad test; investigation and lessons learned.",
     "url": "https://www.nasa.gov/history/apollo-1/"},
    {"group": "Challenge resources", "title": "Apollo 13: Mission Details",
     "detail": "Oxygen tank explosion on the flight to the Moon; investigation.",
     "url": "https://www.nasa.gov/history/apollo-13-mission-details/"},
    {"group": "Challenge resources", "title": "25 Years Ago: Fire Aboard Space Station Mir",
     "detail": "1997 fire from an oxygen generator failure.",
     "url": "https://www.nasa.gov/history/25-years-ago-fire-aboard-space-station-mir/"},
    {"group": "Challenge resources", "title": "Fireman's Air Tanks (NASA Spinoff)",
     "detail": "1970s spacesuit technology adapted for firefighters' air tanks.",
     "url": "https://spinoff.nasa.gov/node/9582"},
    {"group": "Challenge resources", "title": "Fire Detector (NASA Spinoff)",
     "detail": "Detector that tells smoke from dust, with fewer nuisance alarms.",
     "url": "https://spinoff.nasa.gov/node/9407"},
    {"group": "Challenge resources", "title": "New Technology for the Fire Attire (NASA Spinoff)",
     "detail": "Spacesuit materials applied to firefighter clothing.",
     "url": "https://spinoff.nasa.gov/node/9918"},
    {"group": "Challenge resources", "title": "Challenge resources: Flame in Freefall",
     "detail": "NASA Space Apps Challenge resource list for this challenge.",
     "url": "https://www.spaceappschallenge.org/2026/challenges/flame-in-freefall/?tab=resources"},
    # --- Apollo 1 fire documents (combustion-relevant only) ---
    {"group": "Apollo 1 fire documents", "title": "Report of the Apollo 204 Review Board",
     "detail": "Chronology and cause of the fire: three stages, nylon netting and Velcro as fuel.",
     "url": NASA+"missions/apollo/apollo-1/report-of-the-apollo-204-review-board/"},
    {"group": "Apollo 1 fire documents", "title": "Apollo 204 Review Board summary",
     "detail": "Findings, determinations and recommendations.",
     "url": NASA+"missions/apollo/apollo-1/apollo-204-review-board-summary/"},
    {"group": "Apollo 1 fire documents", "title": "Apollo 204 Review Board summary (PDF)",
     "detail": "Board summary as published.",
     "url": APOLLO1+"Apollo204/summary.pdf"},
    {"group": "Apollo 1 fire documents", "title": "Senate Report 956: Apollo 204 Accident (PDF, 1968)",
     "detail": "100% oxygen test atmosphere, combustible material control, cabin rupture about 15 s after the fire call.",
     "url": APOLLO1+"as204_senate_956.pdf"},
    {"group": "Apollo 1 fire documents", "title": "NASA response to the Review Board findings",
     "detail": "Restricted combustible materials, water-based extinguisher, 100% oxygen tests defined as hazardous.",
     "url": NASA+"missions/apollo/apollo-1/nasa-response-to-findings/"},
    # --- Papers and fact sheets linked from the PSI investigation pages ---
    {"group": "Papers linked from PSI pages", "title": "SAFFIRE (NTRS 20170000230)",
     "detail": "Spacecraft Fire Experiment, linked from SAFFIRE-II.",
     "url": "https://ntrs.nasa.gov/api/citations/20170000230/downloads/20170000230.pdf"},
    {"group": "Papers linked from PSI pages", "title": "Cygnus Pressurized Cargo Module fact sheet",
     "detail": "Vehicle that hosted SAFFIRE-II.",
     "url": "https://cdn.northropgrumman.com/-/media/wp-content/uploads/Cygnus-Fact-Sheet-1.pdf"},
    {"group": "Papers linked from PSI pages", "title": "Comparative soot diagnostic hardware (NTRS 19960008413)",
     "detail": "Smoke particle diagnostics, linked from SAME and SAME-R.",
     "url": "https://ntrs.nasa.gov/api/citations/19960008413/downloads/19960008413.pdf"},
    {"group": "Papers linked from PSI pages", "title": "Automated data analysis for consecutive images from droplet combustion experiments",
     "detail": "Image Analysis & Stereology paper, linked from FLEX and FLEX-2.",
     "url": "https://doi.org/10.5566/ias.v31.p137-148"},
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
