import os

import requests


class TMDBError(Exception):
    """Raised when TMDB cannot provide a usable response."""


class TMDBService:
    BASE_URL = "https://api.themoviedb.org/3"

    def __init__(self):
        self.access_token = os.getenv("TMDB_ACCESS_TOKEN")

        if not self.access_token:
            raise RuntimeError("TMDB_ACCESS_TOKEN is not configured.")

    @property
    def headers(self):
        return {
            "Authorization": f"Bearer {self.access_token}",
            "accept": "application/json",
        }

    def _get(self, endpoint, params=None):
        try:
            response = requests.get(
                f"{self.BASE_URL}{endpoint}",
                headers=self.headers,
                params=params,
                timeout=5,
            )
        except requests.RequestException as exc:
            raise TMDBError("TMDB request failed.") from exc

        if response.status_code == 429:
            raise TMDBError("TMDB rate limit reached.")

        if response.status_code >= 500:
            raise TMDBError("TMDB is temporarily unavailable.")

        if response.status_code != 200:
            raise TMDBError("TMDB returned an unexpected response.")

        try:
            return response.json()
        except ValueError as exc:
            raise TMDBError("TMDB returned malformed data.") from exc

    def search_movies(self, query, page=1):
        return self._get(
            "/search/movie",
            params={
                "query": query,
                "page": page,
                "include_adult": False,
                "language": "en-US",
            },
        )

    def get_movie_details(self, tmdb_id):
        return self._get(
            f"/movie/{tmdb_id}",
            params={
                "language": "en-US",
                "append_to_response": "credits",
            },
        )

    def search_person(self, query):
        return self._get(
            "/search/person",
            params={
                "query": query,
                "language": "en-US",
            },
        )

    def discover_movies(self, **filters):
        return self._get(
            "/discover/movie",
            params={
                "language": "en-US",
                "include_adult": False,
                **filters,
            },
        )