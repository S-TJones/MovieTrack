class AIValidationError(ValueError):
	pass


_SEARCH_FIELDS = {
	"intent",
	"genres",
	"year_from",
	"year_to",
	"cast",
	"director",
	"keywords",
}


def _validate_string_list(value, field_name, maximum=20):
	if not isinstance(value, list) or len(value) > maximum:
		raise AIValidationError(f"{field_name} must be a list of strings.")

	cleaned = []
	for item in value:
		if not isinstance(item, str) or not item.strip() or len(item) > 100:
			raise AIValidationError(f"{field_name} must contain short strings.")
		cleaned.append(item.strip())
	return cleaned


def _validate_year(value, field_name):
	if value is None:
		return None
	if isinstance(value, bool) or not isinstance(value, int):
		raise AIValidationError(f"{field_name} must be an integer or null.")
	if value < 1870 or value > 2100:
		raise AIValidationError(f"{field_name} is outside the supported range.")
	return value


def validate_ai_search_response(payload):
	if not isinstance(payload, dict) or set(payload) != _SEARCH_FIELDS:
		raise AIValidationError("AI search response has an invalid structure.")

	if payload["intent"] != "movie_search":
		raise AIValidationError("AI search intent is not supported.")

	genres = _validate_string_list(payload["genres"], "genres")
	cast = _validate_string_list(payload["cast"], "cast")
	keywords = _validate_string_list(payload["keywords"], "keywords")
	year_from = _validate_year(payload["year_from"], "year_from")
	year_to = _validate_year(payload["year_to"], "year_to")

	director = payload["director"]
	if director is not None:
		if not isinstance(director, str) or not director.strip() or len(director) > 100:
			raise AIValidationError("director must be a short string or null.")
		director = director.strip()

	if year_from is not None and year_to is not None and year_from > year_to:
		raise AIValidationError("year_from must not be after year_to.")

	return {
		"intent": "movie_search",
		"genres": genres,
		"year_from": year_from,
		"year_to": year_to,
		"cast": cast,
		"director": director,
		"keywords": keywords,
	}


def validate_ai_recommendations_response(payload):
	if not isinstance(payload, dict) or set(payload) != {"recommendations"}:
		raise AIValidationError("AI recommendations have an invalid structure.")

	recommendations = payload["recommendations"]
	if not isinstance(recommendations, list) or len(recommendations) > 5:
		raise AIValidationError("recommendations must contain at most five items.")

	validated = []
	for recommendation in recommendations:
		if (
			not isinstance(recommendation, dict)
			or set(recommendation) != {"title", "reason"}
		):
			raise AIValidationError("A recommendation has an invalid structure.")

		title = recommendation["title"]
		reason = recommendation["reason"]
		if not isinstance(title, str) or not title.strip() or len(title) > 255:
			raise AIValidationError("Recommendation titles must be short strings.")
		if not isinstance(reason, str) or not reason.strip() or len(reason) > 500:
			raise AIValidationError("Recommendation reasons must be short strings.")

		validated.append({"title": title.strip(), "reason": reason.strip()})

	return {"recommendations": validated}
