import request from "./api";

export function getRating(movieId) {
  return request(`/movies/${movieId}/rating`);
}

export function createRating(movieId, rating) {
  return request(`/movies/${movieId}/rating`, {
    method: "POST",
    body: JSON.stringify({ rating }),
  });
}

export function updateRating(movieId, rating) {
  return request(`/movies/${movieId}/rating`, {
    method: "PUT",
    body: JSON.stringify({ rating }),
  });
}

export function deleteRating(movieId) {
  return request(`/movies/${movieId}/rating`, { method: "DELETE" });
}