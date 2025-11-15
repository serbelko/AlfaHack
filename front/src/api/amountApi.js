import { request } from "./httpClient";

// GET /api/amount/ - список счетов
export async function getAllAmounts() {
  return request("/api/amount/", {
    method: "GET",
    auth: true,
  });
}

// GET /api/amount?name=string - один счет
export async function getAmountByName(name) {
  const params = new URLSearchParams({ name });
  return request(`/api/amount?${params.toString()}`, {
    method: "GET",
    auth: true,
  });
}

// GET /api/amount/history?name=&from=&to=&type=
export async function getAmountHistory({ name, from, to, type }) {
  const params = new URLSearchParams();
  if (name) params.set("name", name);
  if (from) params.set("from", from);
  if (to) params.set("to", to);
  if (type) params.set("type", type);

  return request(`/api/amount/history?${params.toString()}`, {
    method: "GET",
    auth: true,
  });
}

// POST /api/amount/transaction - добавить транзакцию
export async function addTransaction({ name, type, category, count }) {
  return request("/api/amount/transaction", {
    method: "POST",
    auth: true,
    body: { name, type, category, count },
  });
}
