import React from "react";

function PeriodSelector({ value, onChange }) {
  return (
    <div className="period-selector">
      <button
        type="button"
        className={
          "period-selector__btn" +
          (value === "month" ? " period-selector__btn--active" : "")
        }
        onClick={() => onChange("month")}
      >
        Месяц
      </button>
      <button
        type="button"
        className={
          "period-selector__btn" +
          (value === "year" ? " period-selector__btn--active" : "")
        }
        onClick={() => onChange("year")}
      >
        Год
      </button>
      <button
        type="button"
        className={
          "period-selector__btn" +
          (value === "custom" ? " period-selector__btn--active" : "")
        }
        onClick={() => onChange("custom")}
      >
        Период
      </button>
    </div>
  );
}

export default PeriodSelector;
