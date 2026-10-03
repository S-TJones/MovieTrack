# MovieTrack

MovieTrack is a movie-tracking application designed for a personal film library: users can search the catalog, inspect movie details, maintain a collection, rate titles, and review AI-assisted discovery flows. The system separates user-owned data from external metadata providers: the React frontend talks only to the Flask API, and the API owns TMDB and LLM integration.

## Project structure

- `backend/` — Flask application, SQLAlchemy models, routes, and migrations
- `frontend/` — React + Vite client
- `docs/` — AI evaluation, analytics, and deployment guidance
- `.github/workflows/` — CI workflow for backend and frontend checks
- `docker-compose.yml` — local PostgreSQL container for development

## How to run locally

### 1. Backend configuration

Copy `.env.example` to `backend/.env` and set the required values before running the app.

Required values:

- `JWT_SECRET` or `JWT_SECRET_KEY` — secret for signing access tokens
- `DATABASE_URL` — local PostgreSQL URL; the repo default points to the local Docker container at `localhost:5433`
- `TMDB_ACCESS_TOKEN` — required for live TMDB search and movie metadata
- `FRONTEND_ORIGINS` — comma-separated frontend origins for CORS, e.g. `http://localhost:5173,http://127.0.0.1:5173`

Optional values:

- `LLM_API_KEY` — enables live natural-language parsing; if absent, the AI search route falls back to a standard movie search
- `LLM_BASE_URL` — provider base URL, defaults to OpenAI-compatible endpoints
- `LLM_MODEL` — default `gpt-4o-mini`
- `LLM_TIMEOUT_SECONDS` — default `20`

### 2. Database

Start PostgreSQL locally from the repo root:

```bash
docker compose up -d
```

This exposes PostgreSQL on port `5433` to avoid conflicts with a local database already using `5432`.

### 3. Backend run

From `backend/`:

```bash
python -m venv venv
.\venv\Scripts\Activate.ps1
pip install -r requirements.txt
python -m flask --app run.py db upgrade
python -m flask --app run.py run --host 127.0.0.1 --port 5000
```

For Windows local development, use Flask directly rather than Gunicorn. Gunicorn is for Render/Linux production.

### 4. Frontend run

From `frontend/`:

```bash
npm install
npm run dev -- --host 127.0.0.1
```

The frontend is served at `http://127.0.0.1:5173` and proxies `/api` calls to the Flask backend at port `5000`.

## Configuration notes

- `backend/app/__init__.py` applies CORS based on `FRONTEND_ORIGINS`.
- `backend/run.py` is the correct Flask entry point for Render deployment.
- `gunicorn run:app` is valid for Render; `gunicorn app:app` is not correct for this project because the app object lives in `backend/run.py`.
- `VITE_API_BASE_URL` in the frontend must point to the deployed API, not to `localhost`, in production.

## Testing and verification

Run backend tests with coverage from `backend/`:

```bash
python -m pytest --cov --cov-report=term-missing --cov-report=xml
```

Run frontend checks from `frontend/`:

```bash
npm run build
npm audit --audit-level=moderate
```

CI also runs these checks in GitHub Actions.

## Deployment

### Render backend

Deploy a Render web service with:

- root directory: `backend`
- runtime: Python 3
- build command: `pip install -r requirements.txt`
- start command: `gunicorn run:app --bind 0.0.0.0:$PORT`

Required environment variables:

- `DATABASE_URL`
- `JWT_SECRET`
- `FRONTEND_ORIGINS`
- `TMDB_ACCESS_TOKEN`
- `LLM_API_KEY` if live AI is enabled
- `LLM_BASE_URL`, `LLM_MODEL`, `LLM_TIMEOUT_SECONDS` when using a provider with non-default settings

After deployment, run:

```bash
flask --app run.py db upgrade
```

and confirm the service responds on `/health`.

### Vercel frontend

Create a Vercel project rooted at `frontend` with:

- framework preset: `Vite`
- root directory: `frontend`
- build command: `npm run build`
- output directory: `dist`

Set the frontend environment variable:

- `VITE_API_BASE_URL=https://<your-render-service>.onrender.com/api`

`frontend/vercel.json` is included to route SPA paths back to `index.html` after refresh.

## API highlights

- `POST /api/ai/search` parses a free-form query, validates the model response, and resolves filters against TMDB before returning results.
- `POST /api/ai/recommendations` builds recommendations from user ratings and collection state, with a safe fallback when the LLM is unavailable.
- `GET /api/audit/history` returns only the authenticated user’s audit events.
- `GET /api/analytics/activity?days=30` returns that user’s counts by action and UTC day.

## AI assistance disclosure

This project used AI assistance during implementation and validation:

- OpenAI ChatGPT for reasoning, prompt design, and validation suggestions.
- GitHub Copilot for code completion, refactoring suggestions, and incremental defect reduction.

The AI was used to accelerate implementation, not to replace the application logic or bypass validation. Examples of generated output that was corrected or rejected include:

- prompt-injection inputs that were explicitly rejected by the validation layer instead of being treated as trusted prompt instructions
- invalid JSON payloads from the provider that triggered `AIProviderError` and fallback behavior instead of being accepted blindly
- model output with invented TMDB IDs or unsupported attributes that were rejected by schema validation
- year-range and invalid-year cases that were rejected before being used in TMDB discovery calls

The project remains deliberately conservative: model output is treated as untrusted input until validated.

## AI evaluation summary

The current evaluation set is recorded in `docs/ai/evaluation.md`. The deterministic set contains 12 cases covering:

- valid genre/year/cast parsing
- valid director/year parsing
- ambiguous requests
- prompt injection content
- unsupported intents
- malformed schema values
- invalid year ranges
- invented TMDB IDs

Current result: **12/12 passed**.

## Analytics catalogue and KPI definitions

The audit event catalogue is documented in `docs/analytics/activity-analysis.md` and includes:

- `USER_REGISTERED`
- `LOGIN_SUCCESS`
- `LOGIN_FAILED`
- `LOGOUT`
- `MOVIE_SEARCHED`
- `MOVIE_VIEWED`
- `MOVIE_ADDED_TO_COLLECTION`
- `MOVIE_REMOVED_FROM_COLLECTION`
- `RATING_CREATED`
- `RATING_UPDATED`
- `RATING_DELETED`
- `AI_SEARCH_REQUESTED`
- `AI_RECOMMENDATION_REQUESTED`

KPI definitions:

- `total_events`: count of audit rows in the selected time window
- `by_action`: action totals per event type
- `by_day`: event totals grouped by UTC date
- `window_start` and `window_end`: the analytic range used for the query

The analysis is reproducible via `GET /api/analytics/activity?days=30` and by the deterministic pytest case referenced in the analytics document.

See:

- `docs/ai/evaluation.md`
- `docs/analytics/activity-analysis.md`
- `docs/deployment/production-readiness.md`

## Assumptions

- The app is intended for a single-team demo application rather than a multi-tenant SaaS platform.
- A PostgreSQL database is expected for production and a local Docker PostgreSQL container is sufficient for development.
- The TMDB API is the primary system of record for external movie metadata.
- The LLM provider is optional; the app must still function when it is unavailable, using standard TMDB search and fallback recommendation logic.
- The deployment target is Render + Vercel, as requested for the project environment.

## Deliberate omissions

- No custom domain configuration was added because the hosting provider and project-specific DNS information were intentionally not assumed.
- No production secrets or live deployment URLs are committed to the repo.
- No advanced analytics dashboard, non-essential dashboarding, or AWS/GCP specialization was added beyond the required event taxonomy and activity summary.
- No large production monitoring stack or Docker production orchestration was introduced; the project remains simple and demonstrably deployable.

## Known risks and limitations

- AI recommendation quality is bounded by the supplied validation/evaluation set and by the actual provider quality available at runtime.
- When a provider is unavailable or misconfigured, the app falls back to regular TMDB search/recommendation logic rather than failing hard.
- Render free-tier services may cold-start, which can cause initial latency during a live demo.
- Local Windows `npm ci` may hit file-lock issues in OneDrive-backed `node_modules`; the project CI path is Ubuntu-based and the app itself passes builds in a clean environment.
- If a production `JWT_SECRET` is weak or reused across environments, authentication becomes insecure.

## Final note

This project is intentionally designed to be simple, testable, and deployable without over-engineering. It compiles, passes backend coverage and frontend build checks, and is ready for staging on Render/Vercel once the production environment values are added.
