import { request } from "./httpClient";

export async function getAllAmounts() {
  return request("/api/amount/", {
    method: "GET",
    auth: true,
  });
}

export async function getAmountByName(name) {
  const params = new URLSearchParams();
  if (name) {
    params.set("name", name);
  }
  const query = params.toString();
  const path = query ? `/api/amount?${query}` : "/api/amount";
  return request(path, {
    method: "GET",
    auth: true,
  });
}

export async function getAmountHistory({ name, from, to, type } = {}) {
  const params = new URLSearchParams();
  if (name) {
    params.set("name", name);
  }
  if (from) {
    params.set("from", from);
  }
  if (to) {
    params.set("to", to);
  }
  if (type) {
    params.set("type", type);
  }
  const query = params.toString();
  const path = query ? `/api/amount/history?${query}` : "/api/amount/history";
  return request(path, {
    method: "GET",
    auth: true,
  });
}

export async function getSingleTransaction(params = {}) {
  const search = new URLSearchParams();
  Object.entries(params).forEach(([key, value]) => {
    if (value != null && value !== "") {
      search.set(key, String(value));
    }
  });
  const query = search.toString();
  const path = query
    ? `/api/amount/transaction?${query}`
    : "/api/amount/transaction";
  return request(path, {
    method: "GET",
    auth: true,
  });
}

export async function addTransaction({ name, type, category, count }) {
  return request("/api/amount/transaction", {
    method: "POST",
    auth: true,
    body: { name, type, category, count },
  });
}
