# Production Readiness

The intended hosting target is Render for Flask/PostgreSQL and Vercel for the React SPA. No production environment has been deployed yet; the account, database, service URL, and Vercel origin must be provisioned before deployment can be completed.

## Decisions and resources required

- Create a Render PostgreSQL database and a Render Web Service with root directory `backend`.
- Use build command `pip install -r requirements.txt` and start command `gunicorn run:app`.
- Create a Vercel project with root directory `frontend`, framework Vite, build command `npm run build`, and output directory `dist`.
- Set Vercel `VITE_API_BASE_URL` to `https://<render-service>.onrender.com/api`.
- Provide deployment credentials through provider environment settings. Do not put them in GitHub source or frontend variables.

## Required runtime configuration

Backend secrets/configuration:

- `DATABASE_URL` for the managed PostgreSQL database.
- A randomly generated `JWT_SECRET` (at least 32 bytes); rotate the current local development value.
- `TMDB_ACCESS_TOKEN`.
- `FRONTEND_ORIGINS` as a comma-separated list including the exact Vercel origin and any local development origins.
- `LLM_API_KEY` when live AI is enabled; optionally set `LLM_BASE_URL`, `LLM_MODEL`, and `LLM_TIMEOUT_SECONDS`.

Frontend build configuration:

- `VITE_API_BASE_URL` must point to the deployed API. Vite's current `/api` proxy only works in local development.
- Treat every `VITE_*` value as public; never put provider credentials there.

## Release checks

1. Build the frontend and run `npm audit --audit-level=moderate`.
2. Install backend requirements and run pytest with the 80% coverage gate.
3. Apply Alembic migrations as a release step before routing traffic.
4. Configure HTTPS, allowed origins/reverse proxy, `/health` health checks, logs, and database backups.
5. Verify registration, login, TMDB search, collection/rating operations, AI fallback, and user-scoped audit history against the deployed services.

The development `docker-compose.yml` contains a local database password and publishes a host port. Do not use it as a production database configuration. Replace development credentials and use Render's managed/private database networking before deployment. Run `flask --app run.py db upgrade` from the Render service shell after setting production environment variables and before testing the app.

## CI status

GitHub Actions tests backend coverage and builds/audits the frontend. Render and Vercel can deploy automatically from the connected GitHub branch; this repository does not add a custom deploy workflow because the provider projects and secrets have not been created.
