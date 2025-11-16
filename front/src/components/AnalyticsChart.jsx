import React from "react";
import "./AnalyticsChart.css";

function AnalyticsChart({ incomeData, expensesData, labels, yTicks }) {
  const safeIncome = Array.isArray(incomeData) ? incomeData : [];
  const safeExpenses = Array.isArray(expensesData) ? expensesData : [];
  const safeLabels = Array.isArray(labels) ? labels : [];

  const pointsCount = Math.max(
    safeIncome.length,
    safeExpenses.length,
    safeLabels.length
  );

  if (pointsCount === 0) {
    return (
      <div className="chart-empty">Нет данных для отображения графика</div>
    );
  }

  const ticksArray = Array.isArray(yTicks) && yTicks.length > 0 ? yTicks : [0];
  const maxTick = ticksArray[ticksArray.length - 1];

  const fullWidth = 340;
  const graphWidth = 270;
  const chartHeight = 170;
  const topPadding = 14;
  const bottomPadding = 16;
  const innerHeight = chartHeight - topPadding - bottomPadding;

  const xStep = pointsCount > 1 ? graphWidth / (pointsCount - 1) : 0;

  const normalizeY = (value) => {
    if (!maxTick || maxTick <= 0) {
      return topPadding + innerHeight;
    }
    const ratio = Math.min(Math.max(value / maxTick, 0), 1);
    return topPadding + innerHeight - ratio * innerHeight;
  };

  const incomePoints = safeIncome
    .map((v, index) => {
      const x = index * xStep;
      const y = normalizeY(v);
      return `${x},${y}`;
    })
    .join(" ");

  const expensesPoints = safeExpenses
    .map((v, index) => {
      const x = index * xStep;
      const y = normalizeY(v);
      return `${x},${y}`;
    })
    .join(" ");

  return (
    <div className="chart-container">
      <div className="chart-inner">
        <svg
          className="chart-svg"
          width="100%"
          height={chartHeight}
          viewBox={`0 0 ${fullWidth} ${chartHeight}`}
          preserveAspectRatio="none"
        >
          {ticksArray.map((tick) => {
            const y = normalizeY(tick);
            return (
              <g key={tick}>
                <line
                  x1={0}
                  y1={y}
                  x2={graphWidth}
                  y2={y}
                  stroke="#E5E5EA"
                  strokeDasharray="4 4"
                  strokeWidth="1"
                />
                <text
                  x={fullWidth}
                  y={y - 2}
                  textAnchor="end"
                  fontSize="10"
                  fill="#8E8E93"
                >
                  {tick.toLocaleString("ru-RU", {
                    minimumFractionDigits: 2,
                    maximumFractionDigits: 2,
                  })}
                  Р
                </text>
              </g>
            );
          })}

          {incomePoints && (
            <polyline
              points={incomePoints}
              fill="none"
              stroke="#00C30D"
              strokeWidth="2"
              strokeLinecap="round"
              strokeLinejoin="round"
            />
          )}

          {expensesPoints && (
            <polyline
              points={expensesPoints}
              fill="none"
              stroke="#EF3125"
              strokeWidth="2"
              strokeLinecap="round"
              strokeLinejoin="round"
            />
          )}
        </svg>
      </div>

      <div className="chart-x-axis">
        {safeLabels.map((label) => (
          <div key={label} className="chart-x-label">
            {label}
          </div>
        ))}
      </div>
    </div>
  );
}

export default AnalyticsChart;
