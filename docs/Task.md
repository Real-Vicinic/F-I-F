# Flame in Freefall — Tasks

Status: `[ ]` todo · `[~]` in progress · `[x]` done

## 0. Setup
- [ ] Create GitHub repo `flame-in-freefall`, add teammates
- [ ] Create folder skeleton: `frontend/`, `backend/`, `docs/`
- [ ] Create Neon project; save connection string in GitHub Secrets + local `.env`
- [ ] Enable pgvector extension on Neon
- [ ] `sam init` inside `backend/` (Python 3.12 runtime), first deploy works

## 1. Database (Neon)
- [ ] Schema: `investigations(id, name, family, hardware, fuels, objective_summary, o2_min, o2_max, pressure_psi, airflow, gravity, safety_relevance_score, tags, source_url)`
- [ ] Schema: `experiments(id, investigation_id, variables_json, sensors_json)`
- [ ] Schema: `chunks(id, investigation_id, text, embedding vector(1536))` for RAG
- [ ] Migration file + `scripts/seed.py`

## 2. Data curation
- [ ] Build `backend/data/seed.json` for ~15 key investigations: FLEX, FLEX-2, CFI, CFI-G, BASS, BASS-II, SPICE, SLICE, ACME (6), SAME, SAME-R, BRE, DAFT (noted as smoke-hardware reuse)
- [ ] For each: objectives, fuels (shape/size), test conditions (O₂ %, pressure, airflow), sensors, variables, hardware (CIR / MDCA / MSG), source link to PSI
- [ ] Fire-safety relevance tags: prevention / detection / suppression + crew-environment target
- [ ] Relevance scoring v1 (rule-based) → `safety_relevance_score`
- [ ] Generate embeddings for objective/summary chunks → `chunks` table

## 3. Backend (AWS SAM / Lambda)
- [ ] `GET /investigations` — list, pagination, filters (fuel type, O₂ range, hardware, tag), sorted by relevance
- [ ] `GET /investigations/{id}` — detail + `similar_investigations` (same family/hardware/tags)
- [ ] `GET /search?q=` — full-text search across objectives + metadata
- [ ] `POST /chat` — RAG: top-k chunk retrieval → LLM → grounded answer with cited investigation names
- [ ] CORS: allow Cloudflare Pages origin only
- [ ] Neon pooled connection helper with graceful cold-start init
- [ ] Unit tests for ranking + filters (pytest)

## 4. Frontend (React → Cloudflare Pages)
- [ ] Vite + React scaffold inside `frontend/`
- [ ] Explorer page: ranked investigation cards, filter sidebar, search bar
- [ ] Detail page: metadata grid, conditions summary, "Why it matters for fire safety" block, similar list
- [ ] Compare view: select 2 investigations side-by-side (conditions, fuels, sensors)
- [ ] Chat drawer: streaming Q&A, citations rendered as links to detail pages
- [ ] Scenario preset chips: Spacesuit (100% O₂, 4.3 psi) · Moon Base (~30% O₂, ≤10.2 psi) · ISS-like — auto-filter matching investigations
- [ ] "Partial gravity — data coming soon (LUCI / FM2)" info card
- [ ] Loading / error / empty states

## 5. Deploy & CI (GitHub Actions, dev/prod profiles)
- [ ] Create Neon branches: `dev` and `main` (prod)
- [ ] Set up GitHub Environments `dev` + `prod`; store `NEON_DATABASE_URL` as environment secret in each
- [ ] Configure AWS OIDC provider for GitHub Actions + IAM deploy roles (no long-lived access keys)
- [ ] `.github/workflows/backend.yml` — on push to `backend/**`: pytest → migrate Neon (target branch per env) → `sam deploy` via OIDC
- [ ] `.github/workflows/database.yml` — manual dispatch: run migrations + idempotent `seed.py` against chosen Neon branch
- [ ] Cloudflare Pages: connect repo, root dir `frontend/`, per-environment `VITE_API_URL` (preview → dev API, production → prod API)
- [ ] Branch flow: PR → Pages preview + backend `dev` deploy; merge to `main` → production deploys
- [ ] README: local dev (both folders), env vars table, deploy steps
- [ ] Smoke test checklist against deployed API (both environments)

## 6. Demo prep
- [ ] Demo script: 1) ranked explorer → 2) Moon Base scenario filter → 3) compare BASS vs BASS-II → 4) chat: "Which tests ran at ≥30% O₂ and why does that matter for the Moon Base?"
- [ ] Fallback screen recording
- [ ] Pitch deck (problem → data → dashboard → SI insights → fire safety impact)

## Owners (fill in)
| Area | Owner |
|---|---|
| Data curation | |
| Backend / SAM | |
| Frontend / Pages | |
| SI / RAG | |
| Demo & pitch | |
