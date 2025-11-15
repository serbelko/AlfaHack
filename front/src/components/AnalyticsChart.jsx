import React from "react";

function AnalyticsChart({ hasData }) {
  if (!hasData) {
    return (
      <div className="analytics-chart">
        <span>Данных недостаточно</span>
      </div>
    );
  }

  return (
    <div className="analytics-chart">
      <span>График доходов и расходов (mock)</span>
    </div>
  );
}

export default AnalyticsChart;
