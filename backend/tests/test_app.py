import pytest
import requests
import uuid
from flask_jwt_extended import create_access_token
from sqlalchemy.exc import IntegrityError

from app import create_app
from app.audit.actions import AuditAction
from app.audit.service import create_audit_event
from app.extensions import db
from app.models import AuditEvent, Collection, Genre, Movie, Person, Rating, User
from app.movies.tmdb_service import TMDBError, TMDBService


class QueryWithoutRows:
    def filter_by(self, **filters):
        return self

    def first(self):
        return None


@pytest.fixture
def app():
    app = create_app({
        "TESTING": True,
        "SQLALCHEMY_DATABASE_URI": "sqlite://",
        "JWT_SECRET_KEY": "test-secret-that-is-at-least-32-bytes",
    })

    with app.app_context():
        db.create_all()
        yield app
        db.session.remove()
        db.drop_all()


@pytest.fixture
def user_and_movie(app):
    with app.app_context():
        user = User(email="test@example.com", password_hash="not-used")
        movie = Movie(tmdb_id=123, title="Test movie")
        db.session.add_all([user, movie])
        db.session.commit()
        return user.id, movie.id


def auth_headers(app, user_id):
    with app.app_context():
        token = create_access_token(identity=str(user_id))
    return {"Authorization": f"Bearer {token}"}


def test_create_app():
    app = create_app({"TESTING": True, "SQLALCHEMY_DATABASE_URI": "sqlite://"})

    assert app.testing


def test_health_endpoint(app):
    response = app.test_client().get("/health")

    assert response.status_code == 200
    assert response.get_json() == {"status": "ok"}
    uuid.UUID(response.headers["X-Correlation-ID"])


def test_correlation_id_is_echoed_and_used_by_audit_service(app):
    correlation_id = "client-trace-123"
    response = app.test_client().get(
        "/health",
        headers={"X-Correlation-ID": correlation_id},
    )

    assert response.headers["X-Correlation-ID"] == correlation_id

    with app.test_request_context(
        "/test",
        headers={"X-Correlation-ID": correlation_id},
    ):
        app.preprocess_request()
        event = create_audit_event(
            action=AuditAction.MOVIE_VIEWED,
            resource_type="movie",
            resource_id=0,
            metadata={"cached": True},
        )
        assert event.correlation_id == correlation_id
        assert event.resource_id == "0"
        assert event.metadata_json == {"cached": True}
        assert event in db.session
        db.session.rollback()


def test_audit_service_rejects_unregistered_actions(app):
    with app.app_context():
        with pytest.raises(ValueError):
            create_audit_event(
                action="MOVIE_MADE_UP",
                resource_type="movie",
            )


def test_auth_validation_duplicate_and_current_user(app):
    client = app.test_client()

    assert client.post("/api/auth/register", json={}).status_code == 400
    short_password = client.post(
        "/api/auth/register",
        json={"email": "short@example.com", "password": "short"},
    )
    assert short_password.status_code == 400

    registration = client.post(
        "/api/auth/register",
        json={"email": "person@example.com", "password": "password123"},
    )
    assert registration.status_code == 201
    duplicate = client.post(
        "/api/auth/register",
        json={"email": "person@example.com", "password": "password123"},
    )
    assert duplicate.status_code == 409

    assert client.post("/api/auth/login", json={}).status_code == 400
    invalid_login = client.post(
        "/api/auth/login",
        json={"email": "person@example.com", "password": "incorrect"},
    )
    assert invalid_login.status_code == 401
    with app.app_context():
        failed_login_event = AuditEvent.query.filter_by(
            action=AuditAction.LOGIN_FAILED.value,
        ).one()
        assert failed_login_event.user_id is not None
        assert failed_login_event.correlation_id == (
            invalid_login.headers["X-Correlation-ID"]
        )

    token = registration.get_json()["access_token"]
    current_user = client.get(
        "/api/auth/me",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert current_user.status_code == 200
    assert current_user.get_json()["email"] == "person@example.com"

    missing_user_token = auth_headers(app, 999)
    missing_user = client.get("/api/auth/me", headers=missing_user_token)
    assert missing_user.status_code == 404


def test_collection_not_found_responses(app, user_and_movie):
    user_id, _ = user_and_movie
    client = app.test_client()
    headers = auth_headers(app, user_id)

    missing_movie = client.post("/api/collection/999", headers=headers)
    assert missing_movie.status_code == 404

    empty_collection = client.get("/api/collection", headers=headers)
    assert empty_collection.status_code == 200
    assert empty_collection.get_json() == {"items": []}

    not_in_collection = client.delete("/api/collection/999", headers=headers)
    assert not_in_collection.status_code == 404


def test_rating_missing_and_not_found_responses(app, user_and_movie):
    user_id, _ = user_and_movie
    client = app.test_client()
    headers = auth_headers(app, user_id)

    missing_value = client.post(
        "/api/movies/999/rating",
        json={},
        headers=headers,
    )
    assert missing_value.status_code == 400
    assert missing_value.get_json() == {"error": "Rating is required."}

    missing_movie = client.post(
        "/api/movies/999/rating",
        json={"rating": 4},
        headers=headers,
    )
    assert missing_movie.status_code == 404

    missing_update_value = client.put(
        "/api/movies/999/rating",
        json={},
        headers=headers,
    )
    assert missing_update_value.status_code == 400

    missing_rating_update = client.put(
        "/api/movies/999/rating",
        json={"rating": 4},
        headers=headers,
    )
    assert missing_rating_update.status_code == 404

    missing_rating_get = client.get("/api/movies/999/rating", headers=headers)
    assert missing_rating_get.status_code == 200
    assert missing_rating_get.get_json() == {"rating": None}

    missing_rating_delete = client.delete(
        "/api/movies/999/rating",
        headers=headers,
    )
    assert missing_rating_delete.status_code == 404


def test_movie_search_validation_and_tmdb_errors(app, monkeypatch):
    client = app.test_client()
    assert client.get("/api/movies/search").status_code == 400
    assert client.get(f"/api/movies/search?q={'x' * 101}").status_code == 400

    class FailingSearchService:
        def search_movies(self, query):
            raise TMDBError("TMDB is unavailable.")

    monkeypatch.setattr("app.movies.routes.TMDBService", FailingSearchService)
    response = client.get("/api/movies/search?q=Inception")

    assert response.status_code == 502
    assert response.get_json() == {
        "error": "Movie search is temporarily unavailable."
    }


def test_movie_detail_tmdb_error(app, monkeypatch):
    def fail_import(tmdb_id):
        raise TMDBError("TMDB request failed.")

    monkeypatch.setattr("app.movies.routes.MovieService.get_or_import_movie", fail_import)
    response = app.test_client().get("/api/movies/27205")

    assert response.status_code == 502
    assert response.get_json() == {"error": "TMDB request failed."}


def test_tmdb_service_requires_access_token(monkeypatch):
    monkeypatch.delenv("TMDB_ACCESS_TOKEN", raising=False)

    with pytest.raises(RuntimeError, match="TMDB_ACCESS_TOKEN is not configured"):
        TMDBService()


def test_tmdb_service_builds_requests_for_supported_endpoints(monkeypatch):
    monkeypatch.setenv("TMDB_ACCESS_TOKEN", "test-access-token")
    requests_made = []

    class FakeResponse:
        status_code = 200

        def json(self):
            return {"results": []}

    def fake_get(url, **kwargs):
        requests_made.append((url, kwargs))
        return FakeResponse()

    monkeypatch.setattr("app.movies.tmdb_service.requests.get", fake_get)
    service = TMDBService()

    assert service.search_movies("Inception") == {"results": []}
    assert service.get_movie_details(27205) == {"results": []}
    assert service.search_person("Nolan") == {"results": []}
    assert service.discover_movies(with_genres=28) == {"results": []}

    assert [url for url, _ in requests_made] == [
        "https://api.themoviedb.org/3/search/movie",
        "https://api.themoviedb.org/3/movie/27205",
        "https://api.themoviedb.org/3/search/person",
        "https://api.themoviedb.org/3/discover/movie",
    ]
    assert requests_made[0][1]["params"]["query"] == "Inception"
    assert requests_made[1][1]["params"]["append_to_response"] == "credits"
    assert requests_made[2][1]["params"]["query"] == "Nolan"
    assert requests_made[3][1]["params"]["with_genres"] == 28
    assert requests_made[0][1]["headers"]["Authorization"] == (
        "Bearer test-access-token"
    )
    assert requests_made[0][1]["timeout"] == 5


def test_tmdb_service_wraps_request_exception(monkeypatch):
    monkeypatch.setenv("TMDB_ACCESS_TOKEN", "test-access-token")

    def raise_connection_error(*args, **kwargs):
        raise requests.ConnectionError("network unavailable")

    monkeypatch.setattr(
        "app.movies.tmdb_service.requests.get",
        raise_connection_error,
    )

    with pytest.raises(TMDBError, match="TMDB request failed"):
        TMDBService().search_movies("Inception")


@pytest.mark.parametrize(
    ("status_code", "expected_message"),
    [
        (429, "TMDB rate limit reached"),
        (503, "TMDB is temporarily unavailable"),
        (404, "TMDB returned an unexpected response"),
    ],
)
def test_tmdb_service_maps_http_errors(
    monkeypatch,
    status_code,
    expected_message,
):
    monkeypatch.setenv("TMDB_ACCESS_TOKEN", "test-access-token")

    class FakeResponse:
        def __init__(self, status):
            self.status_code = status

    monkeypatch.setattr(
        "app.movies.tmdb_service.requests.get",
        lambda *args, **kwargs: FakeResponse(status_code),
    )

    with pytest.raises(TMDBError, match=expected_message):
        TMDBService().search_movies("Inception")


def test_tmdb_service_rejects_malformed_json(monkeypatch):
    monkeypatch.setenv("TMDB_ACCESS_TOKEN", "test-access-token")

    class FakeResponse:
        status_code = 200

        def json(self):
            raise ValueError("invalid JSON")

    monkeypatch.setattr(
        "app.movies.tmdb_service.requests.get",
        lambda *args, **kwargs: FakeResponse(),
    )

    with pytest.raises(TMDBError, match="TMDB returned malformed data"):
        TMDBService().search_movies("Inception")


def test_collection_unique_violation_returns_conflict(app, user_and_movie, monkeypatch):
    user_id, movie_id = user_and_movie
    with app.app_context():
        db.session.add(Collection(user_id=user_id, movie_id=movie_id))
        db.session.commit()

    monkeypatch.setattr(Collection, "query", QueryWithoutRows())
    response = app.test_client().post(
        f"/api/collections/{movie_id}",
        headers=auth_headers(app, user_id),
    )

    assert response.status_code == 409
    assert response.get_json() == {
        "error": "Movie is already in your collection."
    }
    with app.app_context():
        assert db.session.query(Collection).count() == 1


def test_rating_unique_violation_returns_conflict(app, user_and_movie, monkeypatch):
    user_id, movie_id = user_and_movie
    with app.app_context():
        db.session.add(Rating(user_id=user_id, movie_id=movie_id, rating=4))
        db.session.commit()

    monkeypatch.setattr(Rating, "query", QueryWithoutRows())
    response = app.test_client().post(
        f"/api/movies/{movie_id}/rating",
        json={"rating": 5},
        headers=auth_headers(app, user_id),
    )

    assert response.status_code == 409
    assert response.get_json() == {
        "error": "You have already rated this movie."
    }
    with app.app_context():
        assert db.session.query(Rating).count() == 1


def test_rating_duplicate_precheck_returns_conflict(app, user_and_movie):
    user_id, movie_id = user_and_movie
    with app.app_context():
        db.session.add(Rating(user_id=user_id, movie_id=movie_id, rating=4))
        db.session.commit()

    response = app.test_client().post(
        f"/api/movies/{movie_id}/rating",
        json={"rating": 5},
        headers=auth_headers(app, user_id),
    )

    assert response.status_code == 409
    assert response.get_json() == {
        "error": "You have already rated this movie."
    }


@pytest.mark.parametrize("rating_value", [6, -1, "excellent"])
def test_create_rating_rejects_invalid_values(app, user_and_movie, rating_value):
    user_id, movie_id = user_and_movie
    response = app.test_client().post(
        f"/api/movies/{movie_id}/rating",
        json={"rating": rating_value},
        headers=auth_headers(app, user_id),
    )

    assert response.status_code == 400
    assert response.get_json() == {
        "error": "Rating must be a number between 0 and 5."
    }


@pytest.mark.parametrize("rating_value", [6, -1, "excellent"])
def test_update_rating_rejects_invalid_values(app, user_and_movie, rating_value):
    user_id, movie_id = user_and_movie
    with app.app_context():
        db.session.add(Rating(user_id=user_id, movie_id=movie_id, rating=4.5))
        db.session.commit()

    response = app.test_client().put(
        f"/api/movies/{movie_id}/rating",
        json={"rating": rating_value},
        headers=auth_headers(app, user_id),
    )

    assert response.status_code == 400
    assert response.get_json() == {
        "error": "Rating must be a number between 0 and 5."
    }


def test_database_rejects_rating_outside_check_constraint(app, user_and_movie):
    user_id, movie_id = user_and_movie
    with app.app_context():
        db.session.add(Rating(user_id=user_id, movie_id=movie_id, rating=6))
        with pytest.raises(IntegrityError):
            db.session.commit()
        db.session.rollback()


def test_core_movie_collection_rating_flow(app, monkeypatch):
    client = app.test_client()

    registration = client.post(
        "/api/auth/register",
        json={"email": "core@example.com", "password": "password123"},
        headers={"X-Correlation-ID": "register-core-flow"},
    )
    assert registration.status_code == 201
    assert registration.headers["X-Correlation-ID"] == "register-core-flow"

    login = client.post(
        "/api/auth/login",
        json={"email": "core@example.com", "password": "password123"},
    )
    assert login.status_code == 200
    headers = {
        "Authorization": f"Bearer {login.get_json()['access_token']}"
    }

    class FakeSearchService:
        def search_movies(self, query):
            assert query == "Inception"
            return {
                "results": [{"id": 27205, "title": "Inception"}],
                "page": 1,
                "total_results": 1,
            }

    monkeypatch.setattr("app.movies.routes.TMDBService", FakeSearchService)
    search = client.get("/api/movies/search?q=Inception")
    assert search.status_code == 200
    assert search.get_json()["results"][0]["id"] == 27205

    with app.app_context():
        db.session.add_all([
            Genre(tmdb_id=28, name="Action"),
            Person(tmdb_id=6193, name="Leonardo DiCaprio"),
        ])
        db.session.commit()

    detail_calls = []

    class FakeDetailsService:
        def get_movie_details(self, tmdb_id):
            detail_calls.append(tmdb_id)
            return {
                "id": tmdb_id,
                "title": "Inception",
                "original_title": "Inception",
                "overview": "A dream within a dream.",
                "release_date": "2010-07-16",
                "genres": [
                    {"id": 28, "name": "Action"},
                    {"id": 12, "name": "Adventure"},
                ],
                "credits": {
                    "cast": [
                        {"id": 6193, "name": "Leonardo DiCaprio"},
                        {"id": 1, "name": "New Cast Member"},
                    ],
                    "crew": [
                        {"id": 525, "name": "Christopher Nolan", "job": "Director"},
                        {"id": 2, "name": "Writer", "job": "Writer"},
                    ],
                },
            }

    monkeypatch.setattr("app.movies.service.TMDBService", FakeDetailsService)
    first_movie_response = client.get("/api/movies/27205")
    second_movie_response = client.get("/api/movies/27205")
    assert first_movie_response.status_code == 200
    assert second_movie_response.status_code == 200
    assert first_movie_response.get_json()["title"] == "Inception"
    assert first_movie_response.get_json()["genres"] == [
        {"id": 1, "tmdb_id": 28, "name": "Action"},
        {"id": 2, "tmdb_id": 12, "name": "Adventure"},
    ]
    assert first_movie_response.get_json()["cast"][0]["name"] == "Leonardo DiCaprio"
    assert first_movie_response.get_json()["directors"][0]["name"] == "Christopher Nolan"
    assert detail_calls == [27205]
    movie_id = first_movie_response.get_json()["id"]

    add_response = client.post(
        f"/api/collection/{movie_id}",
        headers=headers,
    )
    assert add_response.status_code == 201
    duplicate_response = client.post(
        f"/api/collection/{movie_id}",
        headers=headers,
    )
    assert duplicate_response.status_code == 409

    collection_response = client.get("/api/collection", headers=headers)
    assert collection_response.status_code == 200
    assert collection_response.get_json()["items"][0]["title"] == "Inception"
    remove_response = client.delete(
        f"/api/collection/{movie_id}",
        headers=headers,
    )
    assert remove_response.status_code == 204
    assert remove_response.data == b""

    create_rating_response = client.post(
        f"/api/movies/{movie_id}/rating",
        json={"rating": 4.5},
        headers=headers,
    )
    assert create_rating_response.status_code == 201
    assert create_rating_response.get_json()["rating"] == 4.5

    get_rating_response = client.get(
        f"/api/movies/{movie_id}/rating",
        headers=headers,
    )
    assert get_rating_response.status_code == 200
    assert get_rating_response.get_json()["rating"] == 4.5

    update_rating_response = client.put(
        f"/api/movies/{movie_id}/rating",
        json={"rating": 5},
        headers=headers,
    )
    assert update_rating_response.status_code == 200
    assert update_rating_response.get_json()["rating"] == 5

    delete_rating_response = client.delete(
        f"/api/movies/{movie_id}/rating",
        headers=headers,
    )
    assert delete_rating_response.status_code == 204
    assert delete_rating_response.data == b""

    with app.app_context():
        registered_event = AuditEvent.query.filter_by(
            action=AuditAction.USER_REGISTERED.value,
        ).one()
        assert registered_event.correlation_id == "register-core-flow"
        recorded_actions = {
            event.action for event in AuditEvent.query.all()
        }
        assert {
            AuditAction.LOGIN_SUCCESS.value,
            AuditAction.MOVIE_SEARCHED.value,
            AuditAction.MOVIE_VIEWED.value,
            AuditAction.MOVIE_ADDED_TO_COLLECTION.value,
            AuditAction.MOVIE_REMOVED_FROM_COLLECTION.value,
            AuditAction.RATING_CREATED.value,
            AuditAction.RATING_UPDATED.value,
            AuditAction.RATING_DELETED.value,
        } <= recorded_actions
