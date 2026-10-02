import request from "./api";

export function searchWithAI(query) {
  return request("/ai/search", {
    method: "POST",
    body: JSON.stringify({ query }),
  });
}

export function getRecommendations() {
  return request("/ai/recommendations", { method: "POST" });
}