import request from "./api";

export function getCollection() {
  return request("/collections");
}

export function addToCollection(movieId) {
  return request(`/collections/${movieId}`, { method: "POST" });
}

export function removeFromCollection(movieId) {
  return request(`/collections/${movieId}`, { method: "DELETE" });
}