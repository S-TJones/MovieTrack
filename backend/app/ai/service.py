import json
import os

import requests

from ..extensions import db
from ..models import Collection, Rating
from ..movies.tmdb_service import TMDBService
from .prompts import (
	AI_RECOMMENDATIONS_SYSTEM_PROMPT,
	AI_SEARCH_SYSTEM_PROMPT,
)
from .schemas import (
	AIValidationError,
	validate_ai_recommendations_response,
	validate_ai_search_response,
)


class AIProviderError(Exception):
	pass


class AIRateLimitError(AIProviderError):
	pass


class LLMClient:
	def __init__(self):
		self.api_key = os.getenv("LLM_API_KEY")
		self.base_url = os.getenv(
			"LLM_API_BASE_URL",
			"https://api.openai.com/v1",
		).rstrip("/")
		self.model = os.getenv("LLM_MODEL", "gpt-4o-mini")

	def complete_json(self, system_prompt, data):
		if not self.api_key:
			raise AIProviderError("LLM_API_KEY is not configured.")

		try:
			response = requests.post(
				f"{self.base_url}/chat/completions",
				headers={
					"Authorization": f"Bearer {self.api_key}",
					"Content-Type": "application/json",
				},
				json={
					"model": self.model,
					"messages": [
						{"role": "system", "content": system_prompt},
						{
							"role": "user",
							"content": json.dumps(data, ensure_ascii=True),
						},
					],
					"response_format": {"type": "json_object"},
					"temperature": 0,
				},
				timeout=20,
			)
		except requests.Timeout as exc:
			raise TimeoutError("LLM request timed out.") from exc
		except requests.RequestException as exc:
			raise AIProviderError("LLM request failed.") from exc

		if response.status_code == 429:
			raise AIRateLimitError("LLM rate limit reached.")
		if response.status_code != 200:
			raise AIProviderError("LLM returned an unexpected response.")

		try:
			content = response.json()["choices"][0]["message"]["content"]
			payload = json.loads(content)
		except (KeyError, IndexError, TypeError, ValueError) as exc:
			raise AIValidationError("LLM returned invalid JSON output.") from exc

		return payload

	def parse_search(self, query):
		payload = self.complete_json(
			AI_SEARCH_SYSTEM_PROMPT,
			{"query": query},
		)
		return validate_ai_search_response(payload)

	def parse_recommendations(self, user_preferences):
		payload = self.complete_json(
			AI_RECOMMENDATIONS_SYSTEM_PROMPT,
			{"user_preferences": user_preferences},
		)
		return validate_ai_recommendations_response(payload)


class AIService:
	def __init__(self, llm_client=None, tmdb_service=None):
		self.llm = llm_client or LLMClient()
		self.tmdb = tmdb_service or TMDBService()

	def search(self, query):
		try:
			filters = self.llm.parse_search(query)
		except (AIProviderError, AIValidationError, TimeoutError):
			result = self.tmdb.search_movies(query)
			return {
				"filters": None,
				"fallback": True,
				"results": result.get("results", []),
			}

		result = self._search_with_filters(query, filters)
		return {
			"filters": filters,
			"fallback": False,
			"results": result.get("results", []),
		}

	def _search_with_filters(self, query, filters):
		tmdb_filters = {"sort_by": "popularity.desc"}
		matched_filter = False

		if filters["genres"]:
			genres = self.tmdb.get_movie_genres().get("genres", [])
			genre_ids = self._resolve_names(filters["genres"], genres)
			if not genre_ids:
				return {"results": []}
			tmdb_filters["with_genres"] = ",".join(map(str, genre_ids))
			matched_filter = True

		if filters["cast"]:
			cast_ids = self._resolve_people(filters["cast"])
			if not cast_ids:
				return {"results": []}
			tmdb_filters["with_cast"] = ",".join(map(str, cast_ids))
			matched_filter = True

		if filters["director"]:
			director_ids = self._resolve_people(
				[filters["director"]],
				department="Directing",
			)
			if not director_ids:
				return {"results": []}
			tmdb_filters["with_crew"] = ",".join(map(str, director_ids))
			matched_filter = True

		if filters["keywords"]:
			keyword_data = []
			for keyword in filters["keywords"]:
				keyword_data.extend(
					self.tmdb.search_keywords(keyword).get("results", [])
				)
			keyword_ids = self._resolve_names(filters["keywords"], keyword_data)
			if not keyword_ids:
				return {"results": []}
			tmdb_filters["with_keywords"] = ",".join(map(str, keyword_ids))
			matched_filter = True

		if filters["year_from"] is not None:
			tmdb_filters["primary_release_date.gte"] = (
				f"{filters['year_from']}-01-01"
			)
			matched_filter = True
		if filters["year_to"] is not None:
			tmdb_filters["primary_release_date.lte"] = (
				f"{filters['year_to']}-12-31"
			)
			matched_filter = True

		if not matched_filter:
			return self.tmdb.search_movies(query)
		return self.tmdb.discover_movies(**tmdb_filters)

	@staticmethod
	def _resolve_names(names, candidates):
		candidates_by_name = {
			item.get("name", "").casefold(): item["id"]
			for item in candidates
			if isinstance(item.get("id"), int) and item.get("name")
		}
		resolved = []
		for name in names:
			candidate_id = candidates_by_name.get(name.casefold())
			if candidate_id is None:
				return []
			resolved.append(candidate_id)
		return resolved

	def _resolve_people(self, names, department=None):
		resolved = []
		for name in names:
			candidates = self.tmdb.search_person(name).get("results", [])
			match = next(
				(
					item
					for item in candidates
					if item.get("name", "").casefold() == name.casefold()
					and isinstance(item.get("id"), int)
					and (
						department is None
						or item.get("known_for_department") == department
					)
				),
				None,
			)
			if match is None:
				return []
			resolved.append(match["id"])
		return resolved

	def recommendations(self, user_id):
		ratings = Rating.query.filter_by(user_id=user_id).all()
		collection = Collection.query.filter_by(user_id=user_id).all()
		preferences = [
			{
				"title": rating.movie.title,
				"rating": float(rating.rating),
				"genres": [genre.name for genre in rating.movie.genres],
			}
			for rating in ratings[:50]
		]
		excluded_ids = {
			rating.movie.tmdb_id for rating in ratings
		} | {
			item.movie.tmdb_id for item in collection
		}

		try:
			result = self.llm.parse_recommendations(preferences)
		except (AIProviderError, AIValidationError, TimeoutError):
			return self._fallback_recommendations(ratings, excluded_ids)

		recommendations = []
		seen_ids = set(excluded_ids)
		for suggestion in result["recommendations"]:
			candidates = self.tmdb.search_movies(suggestion["title"]).get(
				"results",
				[],
			)
			match = next(
				(
					item
					for item in candidates
					if item.get("title", "").casefold()
					== suggestion["title"].casefold()
					and isinstance(item.get("id"), int)
					and item["id"] not in seen_ids
				),
				None,
			)
			if match is None:
				continue
			seen_ids.add(match["id"])
			recommendations.append({
				"tmdb_id": match["id"],
				"title": match["title"],
				"poster_path": match.get("poster_path"),
				"reason": suggestion["reason"],
			})

		return {"fallback": False, "recommendations": recommendations}

	def _fallback_recommendations(self, ratings, excluded_ids):
		genre_ids = sorted({
			genre.tmdb_id
			for rating in ratings
			if float(rating.rating) >= 4
			for genre in rating.movie.genres
		})
		filters = {"sort_by": "popularity.desc"}
		if genre_ids:
			filters["with_genres"] = ",".join(map(str, genre_ids))

		result = self.tmdb.discover_movies(**filters)
		recommendations = []
		for movie in result.get("results", []):
			tmdb_id = movie.get("id")
			if not isinstance(tmdb_id, int) or tmdb_id in excluded_ids:
				continue
			recommendations.append({
				"tmdb_id": tmdb_id,
				"title": movie.get("title", ""),
				"poster_path": movie.get("poster_path"),
				"reason": "Popular movie matching genres you have rated highly.",
			})

		return {"fallback": True, "recommendations": recommendations[:5]}
