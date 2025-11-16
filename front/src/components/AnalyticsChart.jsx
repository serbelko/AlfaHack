import React from "react";
import "./AnalyticsChart.css";

function AnalyticsChart({ incomeData = [], expensesData = [], labels = [] }) {
  const maxValue = Math.max(...incomeData, ...expensesData);
  const minValue = 0;
  const range = maxValue - minValue;
  
  const gridLines = [
    maxValue,
    maxValue * 0.75,
    maxValue * 0.5,
    maxValue * 0.25,
    0
  ];

  const formatValue = (value) => {
    return new Intl.NumberFormat('ru-RU', {
      minimumFractionDigits: 2,
      maximumFractionDigits: 2,
    }).format(value) + '₽';
  };

  const getYPosition = (value) => {
    return ((maxValue - value) / range) * 186;
  };

  const createPath = (data) => {
    if (!data || data.length === 0) return "";
    
    const xStep = 254 / (data.length - 1);
    const points = data.map((value, index) => {
      const x = index * xStep;
      const y = getYPosition(value);
      return `${x},${y}`;
    });
    
    return `M ${points.join(" L ")}`;
  };

  const incomePath = createPath(incomeData);
  const expensesPath = createPath(expensesData);

  const displayLabels = labels.length > 0 ? labels : 
    incomeData.slice(0, 5).map((_, i) => `${i + 1}`);

  return (
    <div className="analytics-chart">
      <div className="chart-grid">
        {gridLines.map((value, index) => (
          <div
            key={index}
            className="grid-line"
            style={{ top: `${getYPosition(value)}px` }}
          >
            <svg width="273" height="1" viewBox="0 0 274 1" fill="none">
              <path
                d="M0.5 0.5L273.5 0.500024"
                stroke="#A3A3A3"
                strokeLinecap="round"
                strokeDasharray="4 4"
              />
            </svg>
            <span className="grid-label">{formatValue(value)}</span>
          </div>
        ))}
      </div>

      <svg className="chart-svg" width="254" height="186" viewBox="0 0 254 186">
        {incomePath && (
          <path
            d={incomePath}
            stroke="#00C10D"
            strokeWidth="1"
            strokeLinecap="round"
            fill="none"
          />
        )}
        {expensesPath && (
          <path
            d={expensesPath}
            stroke="#EF3125"
            strokeWidth="1"
            strokeLinecap="round"
            fill="none"
          />
        )}
      </svg>

      <div className="chart-x-labels">
        {displayLabels.map((label, index) => (
          <span key={index} className="x-label">
            {label}
          </span>
        ))}
      </div>
    </div>
  );
}

export default AnalyticsChart;
