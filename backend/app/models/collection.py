from datetime import datetime, timezone

from ..extensions import db


class Collection(db.Model):
    __tablename__ = "collections"

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

    created_at = db.Column(
        db.DateTime(timezone=True),
        nullable=False,
        default=lambda: datetime.now(timezone.utc),
    )

    __table_args__ = (
        db.UniqueConstraint(
            "user_id",
            "movie_id",
            name="uq_collection_user_movie",
        ),
    )

    user = db.relationship(
        "User",
        backref=db.backref(
            "collections",
            lazy="select",
            cascade="all, delete-orphan",
        ),
    )

    movie = db.relationship(
        "Movie",
        backref=db.backref(
            "collections",
            lazy="select",
        ),
    )