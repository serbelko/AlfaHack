import React from "react";
import { useNavigate } from "react-router-dom";
import "./CompetitorCard.css";

function CompetitorCard({ competitor }) {
  const navigate = useNavigate();

  return (
    <div
      className="competitor-card"
      onClick={() => navigate(`/promotion/competitor/${competitor.id}`)}
    >
      <div className="competitor-image"></div>
      <div className="competitor-details">
        <div className="competitor-name">{competitor.name}</div>
        <div className="competitor-subtitle">{competitor.subtitle}</div>
        <div className="competitor-description">{competitor.description}</div>
      </div>
    </div>
  );
}

export default CompetitorCard;
