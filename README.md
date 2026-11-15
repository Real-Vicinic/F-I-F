# Flame in Freefall

SI-powered fire safety dashboard over NASA PSI microgravity combustion investigations. NASA Space Apps 2026.

**Stack:** React (Vite) on Cloudflare Pages · Python Lambda via AWS SAM + API Gateway · Neon Postgres · Groq (`openai/gpt-oss-120b`) for the SI assistant · GitHub Actions.

```
frontend/   React app           backend/src/       Lambda (app, db, scoring, rag)
backend/    SAM app             backend/data/      seed.json (curated investigations)
docs/       MVP / Plan / Tasks  backend/migrations SQL
```

More detail in [`docs/`](docs/): `MVP.md` (scope), `Plan.md` (architecture, CI/CD, SI assistant) and `Task.md` (checklist).

## Setup (once)

1. **Neon:** create a project and copy the *pooled* connection string.
2. **AWS:** create an IAM user (or role) allowed to use CloudFormation, Lambda, API Gateway, IAM (pass role) and S3 (SAM bucket).
3. **Groq:** create one or more API keys at console.groq.com. Make sure the model in `GroqModel` (see below) is available to your account.
4. **GitHub:** Settings → Secrets and variables → Actions. Add these repository secrets (the workflows read them directly):
   | Type | Name | Value |
   |---|---|---|
   | secret | `NEON_DATABASE_URL` | Neon pooled connection string |
   | secret | `AWS_ACCESS_KEY_ID` | deploy user's access key |
   | secret | `AWS_SECRET_ACCESS_KEY` | deploy user's secret key |
   | secret | `GROQ_API_KEYS` | one or more Groq keys separated by `;` (the next key is tried when one fails) |
   | secret | `CLOUDFLARE_API_TOKEN`, `CLOUDFLARE_ACCOUNT_ID` | for the frontend deploy |

   Deployment settings (`AWS_REGION=eu-west-1`, `STAGE=prod`) are set in `.github/workflows/backend.yml`.
5. **Seed data:** Actions → `database` (or `seed`) → Run workflow.
6. **Deploy API:** push to `main`. The run summary prints the API URL. `GROQ_API_KEYS` is passed to the Lambda on **every** deploy, so a missing or empty secret turns the AI assistant off.
7. **Frontend:** the `frontend` workflow builds with `VITE_API_URL` taken from the deployed stack and publishes to Cloudflare Pages (project `flame-in-freefall`). Run it after the first backend deploy.

## SI assistant configuration

| Setting | Where | Value |
|---|---|---|
| Model | `GroqModel` parameter in `backend/template.yaml` (becomes the Lambda's `GROQ_MODEL`; overrides the default in `backend/src/rag.py`) | `openai/gpt-oss-120b` |
| Keys | `GROQ_API_KEYS` GitHub secret (local: `.env`) | `key1;key2` |

To change the model, edit `GroqModel` in `backend/template.yaml` (and `GROQ_MODEL` in `backend/.env.example`) and push to `main`. Pick a model that is listed as available on console.groq.com; Groq retired `llama-3.3-70b-versatile` on 16 Aug 2026 for free and developer-tier accounts.

## Local dev

```bash
# backend
cd backend && pip install -r requirements-dev.txt
cp .env.example .env && export $(grep -v '^#' .env | xargs)
python scripts/migrate.py && python scripts/seed.py
pytest -q
sam build && sam local start-api -p 3000 --parameter-overrides "DatabaseUrl=$DATABASE_URL" "GroqApiKeys=$GROQ_API_KEYS" "GroqModel=$GROQ_MODEL"

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
- SI assistant retrieves chunks with Postgres full-text search and answers only from them, citing investigation names. If Groq cannot answer (no keys, invalid key, retired model, timeout) it falls back to listing the retrieved facts under the heading "SI model unavailable."

## Smoke test

`/health` → `/investigations` returns 20 items → `scenario=moon_base` includes CFI-G → `/compare?ids=bass,flex` → `/export?format=csv` → chat demo question 1 cites CFI-G. The chat check only runs when `SMOKE_CHAT=1`, and it passes even on the fallback answer, so also try a chat question by hand after each deploy.

## Troubleshooting: the SI assistant isn't using Groq

If chat answers start with "SI model unavailable. Relevant indexed facts:", the API is working but Groq did not return an answer. Check, in this order:

1. **Model.** `GroqModel` in `backend/template.yaml` must name a model that is currently available to your Groq account. After changing it, push to `main` so the backend redeploys; editing `rag.py` alone has no effect because the template's value overrides it.
2. **Keys.** The `GROQ_API_KEYS` secret must be set, non-empty and valid, with keys separated by `;`. Every backend deploy overwrites the Lambda's keys with this secret, so an empty secret disables the assistant on the next deploy.
3. **Test a key directly:** `curl https://api.groq.com/openai/v1/models -H "Authorization: Bearer $KEY"` lists the models that key can use.
4. **Timeouts.** Each key is tried in turn with an 18 s limit while the Lambda limit is 25 s, so several dead keys can end in `API 502` instead of the fallback text. Remove invalid keys from the secret.
5. **Reasoning-model replies.** `gpt-oss` models use part of the token budget for reasoning. If answers come back empty, raise `max_tokens` in `rag.py` (1000 or more) or choose a non-reasoning model.

The original `rag.py` does not log Groq errors, so a failing key or model only shows up as the fallback text. Suggested hardening (error logging, a `source` field on `/chat`, a smoke test that requires a real Groq answer) is tracked in `docs/Task.md`, section 6.
