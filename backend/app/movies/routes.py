from flask import Blueprint, jsonify, request

from .tmdb_service import TMDBError, TMDBService
from .service import MovieService


movies_bp = Blueprint("movies", __name__)


@movies_bp.get("/search")
def search_movies():
    query = request.args.get("q", "").strip()

    if not query:
        return {
            "error": "Search query is required."
        }, 400

    if len(query) > 100:
        return {
            "error": "Search query is too long."
        }, 400

    try:
        service = TMDBService()
        results = service.search_movies(query)

        return {
            "results": results.get("results", []),
            "page": results.get("page", 1),
            "total_results": results.get("total_results", 0),
        }, 200

    except TMDBError:
        return {
            "error": "Movie search is temporarily unavailable."
        }, 502
    

@movies_bp.get("/<int:tmdb_id>")
def get_movie(tmdb_id):
    try:
        movie = MovieService.get_or_import_movie(tmdb_id)

    except TMDBError as exc:
        return jsonify({
            "error": str(exc)
        }), 502

    return jsonify({
        "id": movie.id,
        "tmdb_id": movie.tmdb_id,
        "title": movie.title,
        "original_title": movie.original_title,
        "overview": movie.overview,
        "release_date": (
            movie.release_date.isoformat()
            if movie.release_date
            else None
        ),
        "poster_path": movie.poster_path,
        "backdrop_path": movie.backdrop_path,
        "original_language": movie.original_language,
        "tmdb_vote_average": (
            float(movie.tmdb_vote_average)
            if movie.tmdb_vote_average is not None
            else None
        ),
        "tmdb_vote_count": movie.tmdb_vote_count,
        "genres": [
            {
                "id": genre.id,
                "tmdb_id": genre.tmdb_id,
                "name": genre.name,
            }
            for genre in movie.genres
        ],
        "cast": [
            {
                "id": person.id,
                "tmdb_id": person.tmdb_id,
                "name": person.name,
                "profile_path": person.profile_path,
            }
            for person in movie.cast
        ],
        "directors": [
            {
                "id": person.id,
                "tmdb_id": person.tmdb_id,
                "name": person.name,
                "profile_path": person.profile_path,
            }
            for person in movie.directors
        ],
    }), 200