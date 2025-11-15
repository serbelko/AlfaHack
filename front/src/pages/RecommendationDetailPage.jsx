import React from "react";
import { useNavigate } from "react-router-dom";

function RecommendationDetailPage() {
  const navigate = useNavigate();

  return (
    <div>
      <div
        style={{
          display: "flex",
          justifyContent: "space-between",
          marginBottom: 16,
        }}
      >
        <h1 className="page-title">Рекомендация</h1>
        <button
          className="modal-close"
          type="button"
          onClick={() => navigate(-1)}
        >
          ×
        </button>
      </div>

      <div className="card">
        <div className="card-title">Расходы на аренду выросли</div>
        <p style={{ fontSize: 14, lineHeight: 1.4 }}>
          Твой помощник заметил, что расходы по статье «Аренда помещений»
          выросли на 32 % по сравнению с прошлым месяцем. Это может быть связано
          с разовыми платежами, изменением условий договора или некорректной
          категоризацией платежей.
        </p>
        <p style={{ fontSize: 14, lineHeight: 1.4, marginTop: 8 }}>
          Рекомендуем проверить:
          <br />• последние платежи по аренде
          <br />• условия договора (наличие ежегодного повышения)
          <br />• корректность назначения платежей
        </p>
      </div>
    </div>
  );
}

export default RecommendationDetailPage;
