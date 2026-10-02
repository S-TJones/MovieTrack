import { Film } from "lucide-react";
import MovieCard from "./MovieCard";

export default function MovieGrid({ movies = [], emptyTitle = "No films here yet", emptyMessage = "Try another search or add a film to your collection.", renderAction }) {
  if (!movies.length) {
    return (
      <div className="empty-state">
        <Film size={25} aria-hidden="true" />
        <h3>{emptyTitle}</h3>
        <p>{emptyMessage}</p>
      </div>
    );
  }

  return (
    <div className="movie-grid">
      {movies.map((movie) => (
        <MovieCard
          key={movie.tmdb_id ?? movie.id}
          movie={movie}
          action={renderAction?.(movie)}
        />
      ))}
    </div>
  );
}