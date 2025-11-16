import React, { useState } from "react";
import { useNavigate } from "react-router-dom";
import "./RecommendationCard.css";
import recAvatar from "../assets/recommendation/recommend-avatar.png";
import { fetchAIRecommendation } from "../api/aiApi";

function RecommendationCard() {
  const navigate = useNavigate();
  const [loading, setLoading] = useState(false);

  const handleDetails = async () => {
    setLoading(true);

    // пример текста запроса, можешь подставить свои данные
    const textForAI = "Кофейня в центре города, средний чек 350 рублей.";

    const backendMessage = await fetchAIRecommendation(textForAI);

    setLoading(false);

    navigate("/analytics/recommendation", {
      state: { backendMessage },
    });
  };

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

        <button className="recommend-button" onClick={handleDetails}>
          {loading ? "Загрузка..." : "Подробнее"}
          <span className="recommend-button-arrow">›</span>
        </button>
      </div>
    </div>
  );
}

export default RecommendationCard;
