import request from "./api";

export function searchMovies(query) {
  return request(`/movies/search?q=${encodeURIComponent(query)}`);
}

export function getMovie(tmdbId) {
  return request(`/movies/${tmdbId}`);
}