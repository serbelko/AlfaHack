import { request } from "./httpClient";

// Список конкурентов
export async function getCompetitors({ city, niche, price, district }) {
  const params = new URLSearchParams();
  if (city) params.set("city", city);
  if (niche) params.set("niche", niche);
  if (price) params.set("price", price);
  if (district) params.set("district", district);

  return request(`/promotion/competitors?${params.toString()}`, {
    method: "GET",
    auth: true,
  });
}

// Детальный конкурент
export async function getCompetitorById(id) {
  return request(`/promotion/competitor/${id}`, {
    method: "GET",
    auth: true,
  });
}
