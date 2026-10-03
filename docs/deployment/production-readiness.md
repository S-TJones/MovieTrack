# Production Readiness

MovieTrack is currently configured for local development. No production environment has been deployed; choose a hosting provider and provision resources before adding a deployment job.

## Decisions and resources required

- Select a backend host and frontend static host, or a platform that supports both.
- Provision managed PostgreSQL with backups, TLS, and a private network path from the API.
- Configure a stable API origin and frontend routing/rewrite behavior.
- Provide deployment credentials through the chosen provider's secret store. Do not put them in GitHub source or frontend variables.

## Required runtime configuration

Backend secrets/configuration:

- `DATABASE_URL` for the managed PostgreSQL database.
- A randomly generated `JWT_SECRET` (at least 32 bytes); rotate the current local development value.
- `TMDB_ACCESS_TOKEN`.
- `LLM_API_KEY` when live AI is enabled; optionally set `LLM_API_BASE_URL` and `LLM_MODEL`.

Frontend build configuration:

- `VITE_API_BASE_URL` must point to the deployed API. Vite's current `/api` proxy only works in local development.
- Treat every `VITE_*` value as public; never put provider credentials there.

## Release checks

1. Build the frontend and run `npm audit --audit-level=moderate`.
2. Install backend requirements and run pytest with the 80% coverage gate.
3. Apply Alembic migrations as a release step before routing traffic.
4. Configure HTTPS, allowed origins/reverse proxy, health checks, logs, and database backups.
5. Verify registration, login, TMDB search, collection/rating operations, AI fallback, and user-scoped audit history against the deployed services.

The development `docker-compose.yml` contains a local database password and publishes a host port. Do not use it as a production database configuration. Replace development credentials and use managed/private database networking before deployment.

## CI status

GitHub Actions currently tests backend coverage and builds/audits the frontend. Automatic deployment is intentionally not configured until the hosting provider and secret names are selected.
