import { request } from "./httpClient";

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

  const res = await request("/api/ai/message", {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify({ prompt }),
  });

  if (!res) {
    return null;
  }

  const value = (res.segment || res.message || "").toString().toUpperCase();

  if (value.includes("FIN")) return "FIN";
  if (value.includes("MRKT")) return "MRKT";

  return null;
}

export async function fetchAIRecommendation(text) {
  try {
    const res = await request("/api/ai/message", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ prompt: text }),
    });

    return res?.segment || null; // FIN / MRKT либо null
  } catch {
    return null;
  }
}