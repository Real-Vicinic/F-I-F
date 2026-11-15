# Flame in Freefall — Plan

## Architecture

```
┌─────────────────┐         ┌──────────────────────────┐
│  Cloudflare     │  HTTPS  │  AWS API Gateway (REST)  │
│  Pages (React)  │────────▶│  └─ Lambda (Python, SAM) │
└─────────────────┘         └──────┬───────────────────┘
                                   │  SQL (psycopg / asyncpg)
                            ┌──────▼───────────────────┐
                            │  Neon (serverless PG)    │
                            └──────────────────────────┘
```

- **Frontend** (`frontend/`): React + Vite, deployed to Cloudflare Pages. Talks only to the API Gateway URL (env var `VITE_API_URL`).
- **Backend** (`backend/`): AWS SAM project — API Gateway + Python Lambdas, deployed with `sam deploy`. Reads/writes Neon over pooled connection.
- **Database**: Neon Postgres. Schema: `investigations`, `experiments` (test runs), `test_conditions` (O₂ %, pressure, airflow), `chunks` (text plus a generated `tsvector` column with a GIN index, used for RAG retrieval). pgvector/embeddings were planned but not used: retrieval is Postgres full-text search.
- **Repo**: single GitHub repo, `frontend/` and `backend/` as separate top-level folders.

## Repository layout

```
flame-in-freefall/
├── frontend/            # React app → Cloudflare Pages
│   ├── src/
│   │   ├── pages/       # Explorer, Detail, Compare, Chat
│   │   └── components/
│   └── package.json
├── backend/             # AWS SAM app → API Gateway + Lambda
│   ├── template.yaml    # SAM template
│   ├── src/
│   │   ├── handlers/    # get_investigations, get_investigation, search, chat
│   │   ├── db.py        # Neon connection helpers
│   │   └── rag.py       # SI assistant logic (Postgres full-text retrieval + Groq LLM)
│   └── scripts/
│       └── seed.py      # one-time PSI metadata ingest
└── docs/                # MVP.md, Plan.md, Task.md live here
```

## Build phases (hackathon timeline)

**Phase 0 — Foundations (hour 0–2)**
- GitHub repo, folder skeleton, branch protection off, CI stubs
- Neon project + schema, `.env` handling (GitHub Secrets + Cloudflare env vars)
- `sam init` backend skeleton with one working Lambda → API Gateway

**Phase 1 — Data (hour 2–5)**
- Curate investigation metadata (name, family, hardware, fuels, O₂/pressure/airflow ranges, objectives, safety relevance tags) into `backend/data/seed.json`
- `seed.py` loads into Neon; verify with psql
- Relevance scoring v1: rule-based score from safety tags (prevention/detection/suppression weighting)

**Phase 2 — API (hour 5–9)**
- `GET /investigations` (list + filters + ranking)
- `GET /investigations/{id}` (detail + similar investigations)
- `GET /search?q=`
- `POST /chat` (RAG: retrieve top-k investigation chunks via Postgres full-text search → Groq LLM prompt → grounded answer)
- CORS for the Cloudflare Pages origin

**Phase 3 — Frontend (hour 9–16)**
- Explorer page: ranked cards, filter sidebar, search box
- Detail page: metadata grid + "Why it matters for fire safety" SI block
- Compare view: side-by-side two investigations
- Chat drawer: streaming answers with cited investigation names
- Scenario presets (spacesuit / Moon Base / ISS)

**Phase 4 — Deploy & polish (hour 16–20)**
- `sam deploy` to AWS, Cloudflare Pages connect to GitHub `frontend/`
- Env var wiring, smoke tests, demo script
- README: setup + deploy instructions for both folders

**Phase 5 — Demo prep (hour 20–24)**
- Record fallback video, prepare 3 demo questions, rehearse pitch

## Key risks & mitigations

| Risk | Mitigation |
|---|---|
| PSI raw data too large/noisy for hackathon | Use curated metadata subset; link out to PSI for raw downloads |
| LLM hallucination in SI answers | RAG with strict grounding: answer only from retrieved chunks, cite investigation names, "I don't know" fallback |
| Groq model retired or key invalid (the assistant silently drops to the fallback list) | Pin the model in `.github/workflows/backend.yml` (`GROQ_MODEL`), watch Groq's deprecation page, keep several keys in `GROQ_API_KEYS`, and make the smoke test fail when `/chat` is not answered by Groq |
| Cold-start latency on Lambda + Neon | Neon pooled connection in init; keep Lambda memory ≥ 512 MB |
| CORS / env var mismatch between Pages and API | Single `.env.example` per folder, deploy checklist in README |

## CI/CD & environment profiles (GitHub-driven) — original plan

Everything deploys from GitHub — no manual deploys from laptops. Two environment profiles:

| | dev | prod |
|---|---|---|
| Git branch | `develop` | `main` |
| Neon branch | `dev` | `main` |
| AWS SAM stage | `dev` | `prod` |
| Frontend | Cloudflare Pages preview / branch builds | Cloudflare Pages production |

- **No long-lived cloud keys.** GitHub Actions authenticates to AWS via OIDC (`aws-actions/configure-aws-credentials` assuming an IAM role per GitHub Environment). Neon connection strings live in GitHub Environment secrets (`NEON_DATABASE_URL`); the API URL lives in Cloudflare environment variables (`VITE_API_URL`) per Pages environment.
- **`.github/workflows/backend.yml`** — triggers on pushes to `backend/**`: (1) run pytest, (2) run SQL migrations against the target Neon branch, (3) `sam deploy --config-env ${{ vars.SAM_ENV }}` using the OIDC role.
- **`.github/workflows/database.yml`** — manual-dispatch workflow for migrations + idempotent `seed.py` against a chosen Neon branch (useful for refreshing data without a code deploy).
- **Frontend** — Cloudflare Pages' native GitHub integration builds `frontend/` on every push: a preview deployment per PR, production on `main`. No workflow file needed; env vars set per environment in the Cloudflare dashboard so preview builds point at the dev API and production at the prod API.
- **Deploy order & compatibility** — migrations run before the backend deploy; frontend deploys are independent, and the API stays backward-compatible with slightly older frontends so deploy order never breaks the site.

### As implemented

The workflows in `.github/workflows/` differ from the plan above:

- **Auth:** `backend.yml` and `frontend.yml` use repository secrets `AWS_ACCESS_KEY_ID` / `AWS_SECRET_ACCESS_KEY` (not OIDC roles) and read `NEON_DATABASE_URL` from repository secrets (not per-environment secrets).
- **Branches:** `backend.yml` and `frontend.yml` deploy on pushes to `main` only, with `STAGE=prod`. There is no `develop`/dev stack in the workflows yet.
- **Frontend:** `frontend.yml` builds with `VITE_API_URL` read from the deployed CloudFormation stack and publishes to Cloudflare Pages with wrangler (project `flame-in-freefall`).
- **Database:** `database.yml` (migrations + seed) and `PSI-seed.yml` (migrations, seed, optional conditions import) are manual-dispatch.
- **Groq:** `GROQ_API_KEYS` is passed to the Lambda on every `sam deploy`, so an empty or missing secret disables the assistant on the next deploy.

## SI assistant (Groq)

- **Flow:** `POST /chat` → `rag.ask()` → Postgres full-text retrieval (`chunks.tsv`, top 8, or all chunks of one investigation when `investigation_id` is given) → Groq chat completion with a system prompt that allows answers only from the retrieved context and requires `[INVESTIGATION]` citations → response `{answer, citations}`.
- **Configuration:** `GROQ_API_KEYS` (keys separated by `;`, `,` or whitespace; tried in random order until one returns 200) and `GROQ_MODEL`. In AWS, the Lambda's `GROQ_MODEL` comes from the `GroqModel` parameter of `backend/template.yaml`, which overrides the default in `backend/src/rag.py`. **Change the model in `.github/workflows/backend.yml` (`GROQ_MODEL`)**, which passes it to `sam deploy` as `GroqModel=...` on every deploy. Editing only the `Default` in `template.yaml` does not update an existing stack, because SAM reuses the stack's previous parameter values.
- **Model history:** the project started on `llama-3.3-70b-versatile`. Groq retired it on 16 Aug 2026 for free and developer-tier accounts (recommended replacements: `openai/gpt-oss-120b`, `qwen/qwen3.6-27b`), after which every request failed and the assistant showed only the fallback list. The current model is `openai/gpt-oss-120b`.
- **Incident note (Nov 2026):** changing the `GroqModel` default in `template.yaml` did not fix the live app, because `sam deploy` kept the stack's previous parameter value (`llama-3.3-70b-versatile`). The chat showed "Groq does not have model llama-3.3-70b-versatile" until the workflow started passing `GroqModel` explicitly.
- **Fallback behaviour:** if every key fails, the answer is "SI model unavailable (<reason>). Relevant indexed facts:" followed by up to four retrieved chunks, with citations. The reason names the cause (for example "Groq does not have model …", "Groq rejected the API key", "GROQ_API_KEYS is not set on the server"); `/chat` also returns `source` (`groq` or `fallback`) and an `error` code, and the details are logged to CloudWatch. The original `rag.py` logged nothing, which is why the outage was hard to spot.
- **Reasoning models:** `gpt-oss` models spend part of the token budget on reasoning, so keep `max_tokens` generous (1000 or more) and treat an empty reply as a failure.
- **Timeouts:** Lambda is limited to 25 s and API Gateway to 29 s. Keep the per-key Groq timeout short (8 s) so a few dead keys cannot exceed the limit.

## Post-hackathon roadmap

1. Real PSI data pipeline (scheduled Lambda sync)
2. Charts of test conditions (O₂ vs pressure scatter per investigation)
3. Partial-gravity placeholder module (LUCI / FM2 when data lands)
4. Earth spin-offs page (water-mist extinguishers, smoke detectors, firefighter gear)
