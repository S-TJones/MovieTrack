# MovieTrack

MovieTrack is a personal movie library for discovering films, tracking a collection and ratings, and exploring AI-assisted searches and recommendations. Flask owns all TMDB/LLM access; the React client only calls the application API.

## Project Structure

- `backend/` - API and server-side application
- `frontend/` - User interface
- `docs/` - AI evaluation, analytics, and deployment readiness
- `.github/workflows/` - GitHub Actions workflows

## Local development

1. Copy `.env.example` to `backend/.env` and set `JWT_SECRET`, database credentials, and TMDB access token. Set `LLM_API_KEY` to enable live AI parsing; AI search falls back to normal TMDB search without it.
2. Start PostgreSQL from the repository root: `docker compose up -d`. Docker publishes PostgreSQL on `localhost:5433` to avoid a local PostgreSQL service using port 5432.
3. In `backend/`, create/activate the virtual environment, install `requirements.txt`, apply migrations with `python -m flask --app run.py db upgrade`, and start Flask with `python -m flask --app run.py run`.
4. In `frontend/`, run `npm ci` and `npm run dev`. Vite serves the app at `http://127.0.0.1:5173` and proxies `/api` to Flask at port 5000.

Do not commit `.env` files or production credentials.

## Verification

- Backend tests and coverage: from `backend/`, run `python -m pytest --cov --cov-report=term-missing --cov-report=xml`. Coverage must remain at least 80% per `pyproject.toml`.
- Frontend: from `frontend/`, run `npm run build` and `npm audit --audit-level=moderate`.
- GitHub Actions runs backend coverage and frontend install, audit, and production build on pushes and pull requests.

## API highlights

- `POST /api/ai/search` validates structured model output before resolving filters against TMDB; provider or validation failures use the regular movie-search fallback.
- `POST /api/ai/recommendations` checks model-suggested titles against TMDB and has a genre-based fallback.
- `GET /api/audit/history` returns only the authenticated user's audit events.
- `GET /api/analytics/activity?days=30` reports that user's event counts by action and UTC day.

See [`docs/ai/evaluation.md`](docs/ai/evaluation.md), [`docs/analytics/activity-analysis.md`](docs/analytics/activity-analysis.md), and [`docs/deployment/production-readiness.md`](docs/deployment/production-readiness.md).
