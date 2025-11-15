import React from "react";
import { useNavigate, useParams } from "react-router-dom";

function CompetitorDetailPage() {
  const navigate = useNavigate();
  const { id } = useParams();

  const longText =
    "Кофейня «Арома» — сеть точек формата to-go рядом с офисными центрами. Основной поток — сотрудники офисов и студенты. В фокусе стабильное качество, быстрый сервис и понятная линейка напитков. Активно используют акции с кэшбэком и программы лояльности для удержания гостей.";

  return (
    <div>
      <div
        style={{
          display: "flex",
          justifyContent: "space-between",
          marginBottom: 16,
        }}
      >
        <h1 className="page-title">Конкурент #{id}</h1>
        <button
          className="modal-close"
          type="button"
          onClick={() => navigate(-1)}
        >
          ×
        </button>
      </div>

      <div className="card">
        <div
          style={{
            width: "100%",
            height: 160,
            borderRadius: 12,
            backgroundColor: "#e5e7eb",
            marginBottom: 12,
          }}
        />
        <p style={{ fontSize: 14, lineHeight: 1.4 }}>{longText}</p>
      </div>
    </div>
  );
}

export default CompetitorDetailPage;
