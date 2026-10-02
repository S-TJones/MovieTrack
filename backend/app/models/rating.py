from datetime import datetime, timezone

from ..extensions import db


class Rating(db.Model):
    __tablename__ = "ratings"

    id = db.Column(
        db.Integer,
        primary_key=True,
    )

    user_id = db.Column(
        db.Integer,
        db.ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
    )

    movie_id = db.Column(
        db.Integer,
        db.ForeignKey("movies.id", ondelete="CASCADE"),
        nullable=False,
    )

    rating = db.Column(
        db.Numeric(2, 1),
        nullable=False,
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

    __table_args__ = (
        db.UniqueConstraint(
            "user_id",
            "movie_id",
            name="uq_rating_user_movie",
        ),
        db.CheckConstraint(
            "rating >= 0 AND rating <= 5",
            name="ck_rating_range",
        ),
    )

    user = db.relationship(
        "User",
        backref=db.backref(
            "ratings",
            lazy="select",
            cascade="all, delete-orphan",
        ),
    )

    movie = db.relationship(
        "Movie",
        backref=db.backref(
            "ratings",
            lazy="select",
        ),
    )