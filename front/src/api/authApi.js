import { request, setToken, getToken } from "./httpClient";

export async function loginRequest(login, password) {
  const data = await request("/api/auth/login", {
    method: "POST",
    body: { login, password },
  });
  if (!data || !data.token) {
    throw new Error("Некорректный ответ сервера: нет токена");
  }
  setToken(data.token);
  return data.token;
}

export async function getMe() {
  return request("/api/auth/", {
    method: "GET",
    auth: true,
  });
}

export function isAuthenticated() {
  const token = getToken();
  return Boolean(token);
}

export async function logoutRequest() {
  try {
    await request("/api/auth/logout", {
      method: "GET",
      auth: true,
    });
  } finally {
    setToken(null);
  }
}
