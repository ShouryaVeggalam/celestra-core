# Hiring AI

Human-in-the-loop recruiting OS. AI drafts; humans decide. Hosted pilots use **Firebase Auth**; local development keeps `AUTH_MODE=dev`.

## Auth modes

| Mode | When | How |
| --- | --- | --- |
| `AUTH_MODE=dev` | Local only | Bearer token = `User.id` (demo tenant) |
| `AUTH_MODE=firebase` | Staging / production | Firebase ID token → `auth_identities` → `User` |

Firebase UIDs are **not** stored on `User` and never appear in API payloads.

## Run locally

```bash
cd hiring-ai/backend
python3 -m venv .venv
.venv/bin/pip install -e ".[dev]"
cp .env.example .env
# Add GROQ_API_KEY from https://console.groq.com/keys
SEED_DEMO_TENANT=true AUTH_MODE=dev GROQ_API_KEY=gsk_... .venv/bin/uvicorn app.main:app --reload --port 8003

cd hiring-ai/frontend
cp .env.example .env
npm install
npm run dev
```

Open http://127.0.0.1:5177 — Use **Match** to compare a job and candidate with Groq.

## Groq AI

Set on the API:

| Variable | Purpose |
| --- | --- |
| `GROQ_API_KEY` | Required for Match + structure helpers |
| `GROQ_MODEL` | Default `llama-3.3-70b-versatile` |

AI drafts are evidence only. Humans still Import Candidate and Mark hired.

```bash
cd hiring-ai/backend && .venv/bin/pytest
cd hiring-ai/frontend && npm test && npm run build
```

## Share with a client (hosted pilot)

1. **Firebase** — create a project; enable Email/Password + Google; add your Vercel domain as an authorized domain.
2. **Render** — deploy from [`render.yaml`](render.yaml); set `AUTH_MODE=firebase`, Postgres `DATABASE_URL`, `FIREBASE_PROJECT_ID`, HTTPS `CORS_ORIGINS` + `OAUTH_REDIRECT_URL`, strong `INVITE_CODE_PEPPER`, `SEED_DEMO_TENANT=false`. Optional: `GITHUB_TOKEN` for higher sourcing rate limits.
3. **Vercel** — root directory `hiring-ai/frontend`; set `VITE_AUTH_MODE=firebase`, `VITE_HIRING_API_URL`, and `VITE_FIREBASE_*`.
4. Confirm `GET /ready` returns `database=ok` and `firebase=ok`.
5. You sign in first → **Create organization** → Settings → create invite → send the client **app URL + invite code**.

### What your client can do

1. Open the app URL and sign in with Firebase
2. Redeem the invite code
3. Create jobs, discover open-to-work talent (or upload a board CSV), **Import Candidate**, then **Mark hired**

Full checklist: [docs/client/PRODUCTION_CLIENT_LAUNCH.md](docs/client/PRODUCTION_CLIENT_LAUNCH.md).

## Product rules

- No autonomous hire / reject / email / schedule — **Mark hired** is an explicit human action.
- Discoveries are not Candidates until Import.
- Candidate portal routes stay public (no Firebase).
- Design partners never receive `AUTH_MODE=dev` or SQLite.
