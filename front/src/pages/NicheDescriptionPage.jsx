import React from "react";
import { useNavigate } from "react-router-dom";

function NicheDescriptionPage() {
  const navigate = useNavigate();

  const text =
    "Небольшие кофейни to-go с локальным трафиком: основной поток — сотрудники рядом расположенных офисов и жители района. Важно качество напитков, скорость обслуживания и понятные промо-механики.";

  return (
    <div>
      <div
        style={{
          display: "flex",
          justifyContent: "space-between",
          marginBottom: 16,
        }}
      >
        <h1 className="page-title">Описание ниши</h1>
        <button
          className="modal-close"
          type="button"
          onClick={() => navigate(-1)}
        >
          ×
        </button>
      </div>

      <div className="card">
        <p style={{ fontSize: 14, lineHeight: 1.4 }}>{text}</p>
      </div>
    </div>
  );
}

export default NicheDescriptionPage;
