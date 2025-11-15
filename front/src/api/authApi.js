import { request, setToken } from "./httpClient";

// POST /api/auth/login
export async function loginRequest(login, password) {
  const data = await request("/api/auth/login", {
    method: "POST",
    body: { login, password },
  });

  // ТЗ: 201 + { "token": "token" }
  if (!data || !data.token) {
    throw new Error("Некорректный ответ сервера: нет токена");
  }

  setToken(data.token);
  return data.token;
}

// GET /api/auth/
export async function getMe() {
  return request("/api/auth/", {
    method: "GET",
    auth: true,
  });
}

// GET /api/auth/logout
export async function logoutRequest() {
  try {
    await request("/api/auth/logout", {
      method: "GET",
      auth: true,
    });
  } finally {
    // в любом случае токен на фронте забываем
    setToken(null);
  }
}
