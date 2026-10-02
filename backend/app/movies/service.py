from datetime import datetime

from ..extensions import db
from ..models import Genre, Movie, Person
from .tmdb_service import TMDBService


class MovieService:

    @staticmethod
    def get_or_import_movie(tmdb_id):
        # 1. Check our local database first.
        movie = Movie.query.filter_by(tmdb_id=tmdb_id).first()

        if movie:
            return movie

        # 2. Movie isn't cached locally.
        tmdb = TMDBService()
        data = tmdb.get_movie_details(tmdb_id)

        # 3. Create the Movie record.
        movie = Movie(
            tmdb_id=data["id"],
            title=data["title"],
            original_title=data.get("original_title"),
            overview=data.get("overview"),
            poster_path=data.get("poster_path"),
            backdrop_path=data.get("backdrop_path"),
            original_language=data.get("original_language"),
            tmdb_vote_average=data.get("vote_average"),
            tmdb_vote_count=data.get("vote_count"),
        )

        release_date = data.get("release_date")

        if release_date:
            movie.release_date = datetime.strptime(
                release_date,
                "%Y-%m-%d"
            ).date()

        db.session.add(movie)

        # 4. Add genres.
        for genre_data in data.get("genres", []):
            genre = Genre.query.filter_by(
                tmdb_id=genre_data["id"]
            ).first()

            if not genre:
                genre = Genre(
                    tmdb_id=genre_data["id"],
                    name=genre_data["name"],
                )
                db.session.add(genre)

            movie.genres.append(genre)

        # 5. Add cast/directors.
        credits = data.get("credits", {})

        for person_data in credits.get("cast", [])[:20]:
            person = MovieService._get_or_create_person(person_data)

            movie.cast.append(person)

        for person_data in credits.get("crew", []):
            if person_data.get("job") == "Director":
                person = MovieService._get_or_create_person(person_data)

                movie.directors.append(person)

        # 6. Save everything together.
        db.session.commit()

        return movie

    @staticmethod
    def _get_or_create_person(person_data):
        person = Person.query.filter_by(
            tmdb_id=person_data["id"]
        ).first()

        if person:
            return person

        person = Person(
            tmdb_id=person_data["id"],
            name=person_data["name"],
            profile_path=person_data.get("profile_path"),
        )

        db.session.add(person)

        return person