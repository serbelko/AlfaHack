import React from "react";
import "./RecommendationCard.css";
import recAvatar from "../assets/recommendation/recommend-avatar.png";

function RecommendationCard() {
  return (
    <div className="recommend-card">
      <div className="recommend-avatar-wrapper">
        <div className="recommend-avatar-circle">
          <img
            src={recAvatar}
            alt="Рекомендация"
            className="recommend-avatar-image"
          />
        </div>
      </div>
      <div className="recommend-content">
        <div className="recommend-title">Твоя рекомендация</div>
        <div className="recommend-text">Обрати внимание на эквайринг</div>
        <button className="recommend-button" type="button">
          Подробнее
          <span className="recommend-button-arrow">›</span>
        </button>
      </div>
    </div>
  );
}

export default RecommendationCard;
