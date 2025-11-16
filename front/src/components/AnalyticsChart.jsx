import "./AnalyticsChart.css";
import React, { useMemo, useEffect } from "react";

function AnalyticsChart({ incomeData = [], expensesData = [], labels = [] }) {
  const hasData =
    (Array.isArray(incomeData) && incomeData.length > 0) ||
    (Array.isArray(expensesData) && expensesData.length > 0);
  useEffect(() => {
    console.log("GRAPH DATA:", {
      incomeData,
      expensesData,
      labels,
    });
  }, [incomeData, expensesData, labels]);

  const { incomePath, expensesPath, xTicks, viewBoxWidth, viewBoxHeight } =
    useMemo(() => {
      if (!hasData) {
        return {
          incomePath: "",
          expensesPath: "",
          xTicks: [],
          viewBoxWidth: 320,
          viewBoxHeight: 160,
        };
      }

      const length = Math.max(
        incomeData.length,
        expensesData.length,
        labels.length || 0
      );

      const xCount = length > 1 ? length - 1 : 1;
      const width = 320;
      const height = 160;

      const allValues = [
        ...incomeData.filter((v) => typeof v === "number"),
        ...expensesData.filter((v) => typeof v === "number"),
      ];

      let minY = Math.min(...allValues);
      let maxY = Math.max(...allValues);

      if (minY === maxY) {
        // чтобы линии не были идеально прямыми по центру
        minY = minY * 0.9;
        maxY = maxY * 1.1 || 1;
      }

      const paddingTop = 12;
      const paddingBottom = 18;
      const paddingLeft = 4;
      const paddingRight = 4;

      const chartWidth = width - paddingLeft - paddingRight;
      const chartHeight = height - paddingTop - paddingBottom;

      const scaleX = xCount === 0 ? 0 : chartWidth / xCount;
      const scaleY = maxY === minY ? 0 : chartHeight / (maxY - minY);

      const makePath = (data) => {
        if (!data || data.length === 0) return "";

        return data
          .map((value, index) => {
            const x = paddingLeft + index * scaleX;
            const y = paddingTop + chartHeight - (value - minY) * scaleY;
            return `${index === 0 ? "M" : "L"} ${x} ${y}`;
          })
          .join(" ");
      };

      const incomePathLocal = makePath(incomeData);
      const expensesPathLocal = makePath(expensesData);

      const ticks = labels.slice(0, length).map((label, index) => {
        const x = paddingLeft + index * scaleX;
        return { x, label };
      });

      return {
        incomePath: incomePathLocal,
        expensesPath: expensesPathLocal,
        xTicks: ticks,
        viewBoxWidth: width,
        viewBoxHeight: height,
      };
    }, [incomeData, expensesData, labels, hasData]);

  return (
    <div className="analytics-chart">
      {!hasData && (
        <div className="analytics-chart-empty">
          Нет данных за выбранный период
        </div>
      )}

      {hasData && (
        <svg
          className="analytics-chart-svg"
          viewBox={`0 0 ${viewBoxWidth} ${viewBoxHeight}`}
          preserveAspectRatio="none"
        >
          {/* горизонтальные пунктирные линии (3 уровня) */}
          <line
            x1="8"
            y1="32"
            x2={viewBoxWidth - 8}
            y2="32"
            className="analytics-chart-grid-line"
          />
          <line
            x1="8"
            y1="80"
            x2={viewBoxWidth - 8}
            y2="80"
            className="analytics-chart-grid-line"
          />
          <line
            x1="8"
            y1={viewBoxHeight - 32}
            x2={viewBoxWidth - 8}
            y2={viewBoxHeight - 32}
            className="analytics-chart-grid-line"
          />

          {/* линия доходов */}
          {incomePath && (
            <path
              d={incomePath}
              className="analytics-chart-line analytics-chart-line--income"
            />
          )}

          {/* линия расходов */}
          {expensesPath && (
            <path
              d={expensesPath}
              className="analytics-chart-line analytics-chart-line--expenses"
            />
          )}

          {/* подписи по оси X */}
          {xTicks.map((tick, idx) => (
            <text
              key={idx}
              x={tick.x}
              y={viewBoxHeight - 4}
              textAnchor="middle"
              className="analytics-chart-x-label"
            >
              {tick.label}
            </text>
          ))}
        </svg>
      )}
    </div>
  );
}

export default AnalyticsChart;
