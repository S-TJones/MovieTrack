from flask import Blueprint, request

from flask_jwt_extended import get_jwt_identity, jwt_required
from sqlalchemy.exc import IntegrityError
from math import isfinite

from ..extensions import db
from ..models import Movie, Rating


ratings_bp = Blueprint("ratings", __name__)


def _parse_rating(data):
    if "rating" not in data:
        return None, ({"error": "Rating is required."}, 400)

    raw_rating = data["rating"]
    try:
        rating_value = float(raw_rating)
    except (TypeError, ValueError, OverflowError):
        return None, ({
            "error": "Rating must be a number between 0 and 5."
        }, 400)

    if (
        isinstance(raw_rating, bool)
        or not isfinite(rating_value)
        or rating_value < 0
        or rating_value > 5
    ):
        return None, ({
            "error": "Rating must be a number between 0 and 5."
        }, 400)

    return rating_value, None

# Create a rating for a movie
@ratings_bp.post("/movies/<int:movie_id>/rating")
@jwt_required()
def create_rating(movie_id):
    user_id = int(get_jwt_identity())

    data = request.get_json(silent=True) or {}

    rating_value, error_response = _parse_rating(data)
    if error_response:
        return error_response

    movie = db.session.get(Movie, movie_id)

    if not movie:
        return {
            "error": "Movie not found."
        }, 404

    existing_rating = Rating.query.filter_by(
        user_id=user_id,
        movie_id=movie_id,
    ).first()

    if existing_rating:
        return {
            "error": "You have already rated this movie."
        }, 409

    rating = Rating(
        user_id=user_id,
        movie_id=movie_id,
        rating=rating_value,
    )

    db.session.add(rating)
    try:
        db.session.commit()
    except IntegrityError:
        db.session.rollback()
        return {
            "error": "You have already rated this movie."
        }, 409

    return {
        "message": "Rating created.",
        "rating": float(rating.rating),
    }, 201

# Update a rating for a movie
@ratings_bp.put("/movies/<int:movie_id>/rating")
@jwt_required()
def update_rating(movie_id):
    user_id = int(get_jwt_identity())

    data = request.get_json(silent=True) or {}

    rating_value, error_response = _parse_rating(data)
    if error_response:
        return error_response

    rating = Rating.query.filter_by(
        user_id=user_id,
        movie_id=movie_id,
    ).first()

    if not rating:
        return {
            "error": "Rating not found."
        }, 404

    rating.rating = rating_value

    db.session.commit()

    return {
        "message": "Rating updated.",
        "rating": float(rating.rating),
    }, 200


# Delete a rating for a movie
@ratings_bp.delete("/movies/<int:movie_id>/rating")
@jwt_required()
def delete_rating(movie_id):
    user_id = int(get_jwt_identity())

    rating = Rating.query.filter_by(
        user_id=user_id,
        movie_id=movie_id,
    ).first()

    if not rating:
        return {
            "error": "Rating not found."
        }, 404

    db.session.delete(rating)
    db.session.commit()

    return "", 204

# Get the User's rating for a movie
@ratings_bp.get("/movies/<int:movie_id>/rating")
@jwt_required()
def get_rating(movie_id):
    user_id = int(get_jwt_identity())

    rating = Rating.query.filter_by(
        user_id=user_id,
        movie_id=movie_id,
    ).first()

    if not rating:
        return {
            "rating": None
        }, 200

    return {
        "rating": float(rating.rating),
        "created_at": rating.created_at.isoformat(),
        "updated_at": rating.updated_at.isoformat(),
    }, 200