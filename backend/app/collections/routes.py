from flask import Blueprint, g, jsonify

from flask_jwt_extended import get_jwt_identity, jwt_required
from sqlalchemy.exc import IntegrityError

from ..audit.actions import AuditAction
from ..audit.service import create_audit_event
from ..extensions import db
from ..models import Collection, Movie


collections_bp = Blueprint("collections", __name__)


@collections_bp.get("")
@jwt_required()
def get_collection():
    user_id = int(get_jwt_identity())

    collections = (
        Collection.query
        .filter_by(user_id=user_id)
        .order_by(Collection.created_at.desc())
        .all()
    )

    return jsonify({
        "items": [
            {
                "id": item.id,
                "movie_id": item.movie_id,
                "tmdb_id": item.movie.tmdb_id,
                "title": item.movie.title,
                "poster_path": item.movie.poster_path,
                "added_at": item.created_at.isoformat(),
            }
            for item in collections
        ]
    }), 200

# Add a movie to the user's collection
@collections_bp.post("/<int:movie_id>")
@jwt_required()
def add_to_collection(movie_id):
    user_id = int(get_jwt_identity())

    movie = db.session.get(Movie, movie_id)

    if not movie:
        return jsonify({
            "error": "Movie not found."
        }), 404

    existing = Collection.query.filter_by(
        user_id=user_id,
        movie_id=movie_id,
    ).first()

    if existing:
        return jsonify({
            "error": "Movie is already in your collection."
        }), 409

    collection_item = Collection(
        user_id=user_id,
        movie_id=movie_id,
    )

    db.session.add(collection_item)
    create_audit_event(
        user_id=user_id,
        action=AuditAction.MOVIE_ADDED_TO_COLLECTION,
        resource_type="movie",
        resource_id=movie.id,
        correlation_id=g.correlation_id,
    )
    try:
        db.session.commit()
    except IntegrityError:
        db.session.rollback()
        return jsonify({
            "error": "Movie is already in your collection."
        }), 409

    return jsonify({
        "message": "Movie added to collection."
    }), 201

# Remove a movie from the user's collection
@collections_bp.delete("/<int:movie_id>")
@jwt_required()
def remove_from_collection(movie_id):
    user_id = int(get_jwt_identity())

    collection_item = Collection.query.filter_by(
        user_id=user_id,
        movie_id=movie_id,
    ).first()

    if not collection_item:
        return jsonify({
            "error": "Movie is not in your collection."
        }), 404

    db.session.delete(collection_item)
    create_audit_event(
        user_id=user_id,
        action=AuditAction.MOVIE_REMOVED_FROM_COLLECTION,
        resource_type="movie",
        resource_id=collection_item.movie_id,
        correlation_id=g.correlation_id,
    )
    db.session.commit()

    return "", 204

