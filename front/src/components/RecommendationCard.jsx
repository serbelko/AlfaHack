import React from "react";
import { useNavigate } from "react-router-dom";

function RecommendationCard() {
  const navigate = useNavigate();

  return (
    <div
      className="card"
      style={{
        backgroundColor: "#fee2e2",
        border: "1px solid #fecaca",
      }}
    >
      <div className="card-title" style={{ color: "#b91c1c" }}>
        Твой помощник обнаружил изменения…
      </div>
      <div
        className="card-subtitle"
        style={{ marginBottom: 8, color: "#7f1d1d" }}
      >
        Расходы по аренде выросли по сравнению с прошлым месяцем.
      </div>
      <button
        type="button"
        className="button"
        onClick={() => navigate("/analytics/recommendation")}
      >
        Подробнее
      </button>
    </div>
  );
}

export default RecommendationCard;
