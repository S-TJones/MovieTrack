 # MovieTrack Frontend

 React and Vite client for the MovieTrack Flask API.

 ## Run locally

 1. Start PostgreSQL from the repository root with `docker compose up -d`.
 2. Start the Flask API from `backend/` with `python run.py`.
 3. In this directory, install dependencies with `npm install` and start Vite with `npm run dev`.

 Vite proxies `/api` requests to `http://127.0.0.1:5000`. Set `VITE_API_BASE_URL` in `.env` if the API is hosted elsewhere. `.env.example` shows the local default.

 ## Included flows

 - Register and sign in with the Flask API.
 - Search TMDB-backed movie data and view movie details.
 - Add/remove collection entries and create/update/delete personal ratings.
 - Search using natural language and request recommendations from the AI endpoints.
 - View the signed-in user's audit history.

 React communicates with the Flask API through `src/services/`; provider and TMDB credentials remain on the backend.
