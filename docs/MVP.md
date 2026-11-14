# Flame in Freefall — MVP

SI-powered fire safety insights dashboard built on NASA's Physical Science Informatics (PSI) combustion database.

## Goal (hackathon MVP)

A working web dashboard that lets a user **find, compare, and understand** microgravity combustion investigations relevant to fire safety in crewed space environments — with an SI assistant that summarizes and interprets the data in plain language.

## In scope for MVP

1. **Investigation explorer**
   - List all PSI combustion investigations (FLEX, FLEX-2, CFI, CFI-G, BASS, BASS-II, SPICE, SLICE, ACME suite, SAME, SAME-R, BRE, etc.)
   - Each card shows: name, mission/hardware (CIR, MDCA, MSG), fuels, test conditions (O₂ %, pressure, airflow), relevance score to fire safety
2. **Search & filter**
   - Filter by fuel type (solid / liquid / gas), oxygen range, hardware, experiment family
   - Full-text search across objectives and metadata
3. **Fire-safety relevance ranking**
   - Precomputed ranking per investigation against crew-environment needs (prevention / detection / suppression)
4. **Investigation detail page**
   - Summary of objectives, variables, sensors/measurements
   - "How is this relevant to fire safety?" SI-generated explanation
   - Similar investigations ("compare" view for 2 investigations)
5. **SI assistant (chat panel)**
   - Answers questions grounded in the indexed PSI data (RAG over curated summaries + raw metadata)
   - Example: *"Which experiments tested materials at 30%+ oxygen like the planned Moon Base?"*
6. **Moon/Mars context view**
   - Preset scenario filter: spacesuit (100% O₂, 4.3 psi), Moon Base (~30% O₂, ≤10.2 psi), ISS-like Earth atmosphere — showing which investigations bound each scenario
7. **Basic ingest pipeline**
   - Seed script that loads curated investigation metadata into Neon DB (run once, committed to repo)

## Out of scope for MVP (future)

- Real-time PSI API sync / full raw dataset ingestion
- Partial-gravity modeling (no data in PSI yet — noted as "coming soon" in UI)
- User accounts / saved collections
- Earth-application spin-off pages (firefighter gear, smoke detectors) beyond a static info card

## Stack (fixed)

| Layer | Tech | Deploy |
|---|---|---|
| Frontend | React (Vite) | Cloudflare Pages |
| Backend | Python Lambda functions via AWS SAM | API Gateway + Lambda |
| Database | Neon (serverless Postgres) | managed |
| Repo | GitHub, monorepo with `frontend/` and `backend/` as separate top-level folders | GitHub Actions |

## MVP success criteria

- Dashboard loads ranked investigation list in < 2 s
- Filters work across all seeded investigations
- SI assistant answers 3 demo questions correctly, grounded in seeded data, with cited investigation names
- `sam deploy` + Cloudflare Pages deploy both run from a clean clone using only README instructions
