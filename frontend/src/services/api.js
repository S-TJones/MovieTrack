const API_BASE_URL = (import.meta.env.VITE_API_BASE_URL || "/api").replace(/\/$/, "");

function createCorrelationId() {
  return globalThis.crypto?.randomUUID?.() || `${Date.now()}-${Math.random()}`;
}

export default async function request(endpoint, options = {}) {
  const token = localStorage.getItem("access_token");
  const headers = new Headers(options.headers || {});
  headers.set("Accept", "application/json");
  headers.set("X-Correlation-ID", createCorrelationId());

  if (options.body && !headers.has("Content-Type")) {
    headers.set("Content-Type", "application/json");
  }
  if (token) headers.set("Authorization", `Bearer ${token}`);

  const response = await fetch(`${API_BASE_URL}${endpoint}`, {
    ...options,
    headers,
  });

  const correlationId = response.headers.get("X-Correlation-ID");
  let data = null;
  if (response.status !== 204) {
    const contentType = response.headers.get("content-type") || "";
    if (contentType.includes("application/json")) data = await response.json();
  }

  if (!response.ok) {
    const error = new Error(data?.error || "Something went wrong.");
    error.status = response.status;
    error.data = data;
    error.correlationId = correlationId;
    if (response.status === 401 && token) {
      window.dispatchEvent(new Event("movietrack:unauthorized"));
    }
    throw error;
  }

  return data;
}