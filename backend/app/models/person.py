from ..extensions import db


class Person(db.Model):
    __tablename__ = "people"

    id = db.Column(db.Integer, primary_key=True)

    tmdb_id = db.Column(
        db.Integer,
        unique=True,
        nullable=False,
    )

    name = db.Column(
        db.String(255),
        nullable=False,
    )

    profile_path = db.Column(
        db.String(500),
        nullable=True,
    )