# Flame in Freefall

SI-powered fire safety dashboard over NASA PSI microgravity combustion investigations. NASA Space Apps 2026.

**Stack:** React (Vite) on Cloudflare Pages · Python Lambda via AWS SAM + API Gateway · Neon Postgres · Groq (llama-3.3-70b-versatile) for the SI assistant · GitHub Actions (AWS OIDC, no long-lived keys).

```
frontend/   React app           backend/src/       Lambda (app, db, scoring, rag)
backend/    SAM app             backend/data/      seed.json (curated investigations)
docs/       MVP / Plan / Tasks  backend/migrations SQL
```

## Setup (once)

1. **Neon:** create a project, branches `main` (prod) and `dev`. Copy each *pooled* connection string.
2. **AWS:** add the GitHub OIDC provider (`token.actions.githubusercontent.com`) and one IAM role per environment trusted for `repo:<owner>/flame-in-freefall:environment:dev|prod`, with permissions for CloudFormation, Lambda, API Gateway, IAM (pass role), S3 (SAM bucket).
3. **GitHub:** create Environments `dev` and `prod`. In each:
   | Type | Name | Value |
   |---|---|---|
   | secret | `NEON_DATABASE_URL` | that env's Neon branch URL |
   | secret | `AWS_ROLE_ARN` | that env's IAM role |
   | secret | `GROQ_API_KEYS` | keys separated by `;` (rotated on 429) |
   | var | `ALLOWED_ORIGIN` | the Pages origin, e.g. `https://flame-in-freefall.pages.dev` (default `*`) |
   | var | `AWS_REGION` | default `eu-west-1` |
4. **Seed data:** Actions → `database` → Run workflow (env `dev`, then `prod`).
5. **Deploy API:** push to `develop` (dev) or `main` (prod). The run summary prints the API URL.
6. **Cloudflare Pages:** connect the repo, root `frontend`, build `npm run build`, output `dist`. Set `VITE_API_URL` per environment (Preview → dev API, Production → prod API).

Branch flow: `develop` → dev stack, `main` → prod stack. Pages builds a preview per PR.

## Local dev

```bash
# backend
cd backend && pip install -r requirements-dev.txt
cp .env.example .env && export $(grep -v '^#' .env | xargs)
python scripts/migrate.py && python scripts/seed.py
pytest -q
sam build && sam local start-api -p 3000 --parameter-overrides "DatabaseUrl=$DATABASE_URL"

# frontend
cd frontend && cp .env.example .env && npm install && npm run dev
```

## API

| Endpoint | Purpose |
|---|---|
| `GET /investigations` | Ranked list. Params: `q fuel hardware family tier tag o2_min scenario focus limit offset`. `scenario` = `iss spacecraft moon_base rover mars_base spacesuit` (filters and re-ranks). `focus` = `all prevention detection suppression` |
| `GET /investigations/{id}` | Detail, same/varied conditions, loaded test conditions, similar investigations |
| `GET /compare?ids=a,b[,c,d]` | Similarities and differences, field by field |
| `GET /environments` | Crew environments with O2 %, psi, O2 partial pressure |
| `GET /coverage` | Per environment, which investigations cover prevention / detection / suppression, plus data gaps |
| `GET /equipment` | Investigations grouped by the control or equipment area they inform |
| `GET /earth` | Applications on Earth |
| `GET /hardware` | Investigations grouped by hardware family |
| `GET /export?kind=investigations\|conditions&format=csv\|json` | Modeling-ready data (accepts the `/investigations` filters) |
| `GET /search?q=` · `POST /chat {question, investigation_id?}` | Full-text search and the SI assistant |
| `GET /meta` · `GET /conditions` · `GET /health` | Scope notes, test conditions, health check |

Frontend: **Explorer** (filters, environment chips, compare, detail) and **Insights** (environments, controls and equipment, Earth applications, hardware, gaps, data export).

## Loading real test conditions

Download conditions from NASA PSI into a CSV (`backend/data/conditions.example.csv` shows the columns), then:
`python backend/scripts/import_conditions.py conditions.csv`. They appear in `/export?kind=conditions` and on detail pages. Run it with each environment's `DATABASE_URL`.

## Notes

- `seed.json` is a curated summary from public NASA descriptions. Only values stated in the challenge brief are numeric (e.g. CFI-G up to 85% O₂); everything else is flagged "not specified" or "to verify". Verify against PSI before presenting figures.
- Relevance score is rule-based (`scoring.py`): prevention/detection/suppression weights plus tags (oxygen variation, solids, spacecraft scale).
- SI assistant retrieves chunks with Postgres full-text search and answers only from them, citing investigation names. Without Groq keys it falls back to listing retrieved facts.

## Smoke test

`/health` → `/investigations` returns 20 items → `scenario=moon_base` includes CFI-G → `/compare?ids=bass,flex` → `/export?format=csv` → chat demo question 1 cites CFI-G.
