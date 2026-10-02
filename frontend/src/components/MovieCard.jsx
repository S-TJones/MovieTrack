import { Link } from "react-router-dom";
import { Star } from "lucide-react";

const IMAGE_BASE = "https://image.tmdb.org/t/p/w500";

export default function MovieCard({ movie, action }) {
  const tmdbId = movie.tmdb_id ?? movie.id;
  const poster = movie.poster_path
    ? `${IMAGE_BASE}${movie.poster_path}`
    : null;
  const year = (movie.release_date || "").slice(0, 4);
  const score = movie.tmdb_vote_average ?? movie.vote_average;

  return (
    <article className="movie-card">
      <Link className="movie-poster-link" to={`/movies/${tmdbId}`} aria-label={`View ${movie.title}`}>
        {poster ? (
          <img className="movie-poster" src={poster} alt={`${movie.title} poster`} loading="lazy" />
        ) : (
          <span className="poster-placeholder" aria-label="No poster available">MT</span>
        )}
      </Link>
      <div className="movie-card-info">
        <Link className="movie-title" to={`/movies/${tmdbId}`}>{movie.title}</Link>
        <div className="movie-card-meta">
          <span>{year || "Release date unknown"}</span>
          {score != null && (
            <span className="movie-score"><Star size={13} fill="currentColor" /> {Number(score).toFixed(1)}</span>
          )}
        </div>
        {action && <div className="movie-card-action">{action}</div>}
      </div>
    </article>
  );
}