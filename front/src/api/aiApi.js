const AI_BASE_URL =
  import.meta.env.VITE_AI_API_BASE_URL || "http://localhost:8001";

function buildBusinessDescription({ city, niche, priceSegment, district }) {
  const parts = [];
  if (city) parts.push(`Город: ${city}`);
  if (district) parts.push(`Район: ${district}`);
  if (niche) parts.push(`Ниша: ${niche}`);
  if (priceSegment) parts.push(`Ценовой сегмент: ${priceSegment}`);
  const description = parts.join("\n").trim();
  if (!description) {
    return "Нет данных о бизнесе. Определи, какие рекомендации дать клиенту: финансовые (FIN) или маркетинговые (MRKT). Ответь только одним словом.";
  }
  return (
    description +
    "\n\nНа основе этих данных определи, какие рекомендации сейчас важнее: финансовые (FIN) или маркетинговые (MRKT). Ответь только одним словом."
  );
}

export async function getRecommendationSegment({
  city,
  niche,
  priceSegment,
  district,
}) {
  const base = AI_BASE_URL.replace(/\/+$/, "");
  const url = `${base}/api/ai/message/mock/`;
  const prompt = buildBusinessDescription({
    city,
    niche,
    priceSegment,
    district,
  });

  try {
    const res = await fetch(url, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({ prompt }),
    });

    if (!res.ok) {
      return null;
    }

    let data = null;
    try {
      data = await res.json();
    } catch {
      data = null;
    }

    if (!data) {
      const text = await res.text();
      const value = String(text || "").toUpperCase();
      if (value.includes("FIN")) return "FIN";
      if (value.includes("MRKT")) return "MRKT";
      return null;
    }

    const value = String(data.segment || data.message || "").toUpperCase();
    if (value.includes("FIN")) return "FIN";
    if (value.includes("MRKT")) return "MRKT";

    return null;
  } catch (error) {
    console.error("AI recommendation request failed", error);
    return null;
  }
}
