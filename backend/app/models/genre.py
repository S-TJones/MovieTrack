from ..extensions import db


class Genre(db.Model):
    __tablename__ = "genres"

    id = db.Column(db.Integer, primary_key=True)

    tmdb_id = db.Column(
        db.Integer,
        unique=True,
        nullable=False,
    )

    name = db.Column(
        db.String(100),
        unique=True,
        nullable=False,
    )