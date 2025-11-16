import React from "react";
import "./PeriodSelector.css";

function PeriodSelector({ value, onChange }) {
  return (
    <div className="period-selector">
      <button
        type="button"
        className={`period-btn ${value === "month" ? "active" : ""}`}
        onClick={() => onChange("month")}
      >
        Месяц
      </button>
      <button
        type="button"
        className={`period-btn ${value === "year" ? "active" : ""}`}
        onClick={() => onChange("year")}
      >
        Год
      </button>
      <button
        type="button"
        className={`period-btn ${value === "custom" ? "active" : ""}`}
        onClick={() => onChange("custom")}
      >
        Период
      </button>
    </div>
  );
}

export default PeriodSelector;
