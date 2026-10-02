from datetime import datetime, timezone

from ..extensions import db


class Movie(db.Model):
    __tablename__ = "movies"

    id = db.Column(db.Integer, primary_key=True)

    tmdb_id = db.Column(
        db.Integer,
        unique=True,
        nullable=False,
        index=True,
    )

    title = db.Column(
        db.String(255),
        nullable=False,
    )

    original_title = db.Column(
        db.String(255),
        nullable=True,
    )

    overview = db.Column(
        db.Text,
        nullable=True,
    )

    release_date = db.Column(
        db.Date,
        nullable=True,
    )

    poster_path = db.Column(
        db.String(500),
        nullable=True,
    )

    backdrop_path = db.Column(
        db.String(500),
        nullable=True,
    )

    original_language = db.Column(
        db.String(10),
        nullable=True,
    )

    tmdb_vote_average = db.Column(
        db.Numeric(4, 2),
        nullable=True,
    )

    tmdb_vote_count = db.Column(
        db.Integer,
        nullable=True,
    )

    created_at = db.Column(
        db.DateTime(timezone=True),
        nullable=False,
        default=lambda: datetime.now(timezone.utc),
    )

    updated_at = db.Column(
        db.DateTime(timezone=True),
        nullable=False,
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
    )

    movie_genres = db.Table(
        "movie_genres",
        db.Column(
            "movie_id",
            db.Integer,
            db.ForeignKey("movies.id", ondelete="CASCADE"),
            primary_key=True,
        ),
        db.Column(
            "genre_id",
            db.Integer,
            db.ForeignKey("genres.id", ondelete="CASCADE"),
            primary_key=True,
        ),
    )


    movie_cast = db.Table(
        "movie_cast",
        db.Column(
            "movie_id",
            db.Integer,
            db.ForeignKey("movies.id", ondelete="CASCADE"),
            primary_key=True,
        ),
        db.Column(
            "person_id",
            db.Integer,
            db.ForeignKey("people.id", ondelete="CASCADE"),
            primary_key=True,
        ),
    )


    movie_directors = db.Table(
        "movie_directors",
        db.Column(
            "movie_id",
            db.Integer,
            db.ForeignKey("movies.id", ondelete="CASCADE"),
            primary_key=True,
        ),
        db.Column(
            "person_id",
            db.Integer,
            db.ForeignKey("people.id", ondelete="CASCADE"),
            primary_key=True,
        ),
    )

    genres = db.relationship(
        "Genre",
        secondary=movie_genres,
        lazy="selectin",
    )

    cast = db.relationship(
        "Person",
        secondary=movie_cast,
        lazy="selectin",
    )

    directors = db.relationship(
        "Person",
        secondary=movie_directors,
        lazy="selectin",
    )