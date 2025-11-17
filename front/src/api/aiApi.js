import { request } from "./httpClient";

/**
 * Отправляет описание бизнеса и получает от бэка сегмент:
 * "FIN" или "MRKT".
 *
 * Если бэк не ответил или вернул что-то странное → вернёт null,
 * тогда фронт покажет шаблон.
 */
export async function getRecommendationSegment({
  city,
  niche,
  priceSegment,
  district,
}) {
  const parts = [];

  if (city) parts.push(`Город: ${city}`);
  if (district) parts.push(`Район: ${district}`);
  if (niche) parts.push(`Ниша: ${niche}`);
  if (priceSegment) parts.push(`Сегмент по чеку: ${priceSegment}`);

  const prompt =
    parts.join(". ") ||
    "Небольшой локальный бизнес. Подскажи, что критичнее сейчас: финансы или маркетинг.";

  let res;
  try {
    res = await request("/api/ai/message", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({ prompt }),
    });
  } catch (e) {
    // Бэк не ответил → фронт работает в режиме заглушки
    console.error("AI request failed", e);
    return null;
  }

  if (!res) {
    return null;
  }

  const value = (res.segment || res.message || "").toString().toUpperCase();

  if (value.includes("FIN")) return "FIN";
  if (value.includes("MRKT")) return "MRKT";

  return null;
}
