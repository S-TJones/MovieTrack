from flask import Flask

from .config import Config
from .extensions import db, migrate, bcrypt, jwt
from .models import User, Movie, Person, Genre, Rating, Collection
from .movies.routes import movies_bp
from .collections.routes import collections_bp
from .ratings.routes import ratings_bp


def create_app(test_config=None):
    app = Flask(__name__)
    app.config.from_object(Config)

    if test_config is not None:
        app.config.update(test_config)

    db.init_app(app)
    migrate.init_app(app, db)
    bcrypt.init_app(app)
    jwt.init_app(app)

    from .auth.routes import auth_bp
    app.register_blueprint(auth_bp, url_prefix="/api/auth")
    app.register_blueprint(movies_bp, url_prefix="/api/movies")
    app.register_blueprint(collections_bp, url_prefix="/api/collections")
    app.register_blueprint(
        collections_bp,
        url_prefix="/api/collection",
        name="collection",
    )
    app.register_blueprint(ratings_bp, url_prefix="/api")
    app.register_blueprint(
        ratings_bp,
        url_prefix="/api/ratings",
        name="ratings_legacy",
    )

    # Health check endpoint
    @app.get("/health")
    def health():
        return {"status": "ok"}, 200

    return app
