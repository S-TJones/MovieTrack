import request from "./api";

export function register(email, password) {
  return request("/auth/register", {
    method: "POST",
    body: JSON.stringify({ email, password }),
  });
}

export async function login(email, password) {
  const data = await request("/auth/login", {
    method: "POST",
    body: JSON.stringify({ email, password }),
  });
  localStorage.setItem("access_token", data.access_token);
  return data;
}

export function getCurrentUser() {
  return request("/auth/me");
}

export function logout() {
  localStorage.removeItem("access_token");
}