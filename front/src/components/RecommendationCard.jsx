import React from "react";
import { useNavigate } from "react-router-dom";
import "./RecommendationCard.css";

function RecommendationCard() {
  const navigate = useNavigate();

  return (
    <div className="recommendation-card">
      <div className="recommendation-icon"></div>
      <div className="recommendation-content">
        <div className="recommendation-title">Твоя рекомендация</div>
        <div className="recommendation-text">Обрати внимание на эквайринг</div>
        <button
          className="recommendation-button"
          onClick={() => navigate("/analytics/recommendation")}
        >
          <span>Подробнее</span>
          <svg width="8" height="14" viewBox="0 0 8 14" fill="none">
            <path
              d="M1 12.3137L6.65685 6.65687L0.999999 1.00001"
              stroke="white"
              strokeWidth="2"
              strokeLinecap="round"
              strokeLinejoin="round"
            />
          </svg>
        </button>
      </div>
    </div>
  );
}

export default RecommendationCard;
