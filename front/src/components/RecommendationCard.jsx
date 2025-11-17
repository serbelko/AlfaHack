import React from "react";
import { useNavigate } from "react-router-dom";
import "./RecommendationCard.css";
import recAvatar from "../assets/recommendation/recommend-avatar.png";

function RecommendationCard({ segment }) {
  const navigate = useNavigate();

  const handleDetails = () => {
    navigate("/analytics/recommendation", {
      state: { segment: segment || null },
    });
  };

  let subtitle = "Обрати внимание на эквайринг";
  if (segment === "FIN") {
    subtitle = "Сейчас критичнее навести порядок в финансах";
  } else if (segment === "MRKT") {
    subtitle = "Сейчас важнее сфокусироваться на клиентах и маркетинге";
  }

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
        <div className="recommend-text">{subtitle}</div>

        <button
          className="recommend-button"
          onClick={handleDetails}
          type="button"
        >
          Подробнее
          <span className="recommend-button-arrow">›</span>
        </button>
      </div>
    </div>
  );
}

export default RecommendationCard;
