import os

from dotenv import load_dotenv

load_dotenv()


def _normalize_database_url(url):
    if url.startswith("postgres://"):
        return url.replace("postgres://", "postgresql+psycopg2://", 1)
    if url.startswith("postgresql://"):
        return url.replace("postgresql://", "postgresql+psycopg2://", 1)
    return url


class Config:
    # SECRET_KEY = os.environ.get("SECRET_KEY")
    JWT_SECRET = os.environ.get("JWT_SECRET")
    JWT_SECRET_KEY = os.environ.get(
        "JWT_SECRET_KEY",
        JWT_SECRET,
    )
    SQLALCHEMY_DATABASE_URI = _normalize_database_url(
        os.environ.get("DATABASE_URL", "sqlite:///movietrack.db")
    )
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    FRONTEND_ORIGINS = os.environ.get(
        "FRONTEND_ORIGINS",
        "http://localhost:5173,http://127.0.0.1:5173",
    )
