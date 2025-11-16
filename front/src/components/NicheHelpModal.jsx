import React from "react";
import "./NicheHelpModal.css";

function NicheHelpModal({ onClose }) {
  const handleOverlayClick = (e) => {
    e.stopPropagation();
    onClose();
  };

  const handleCardClick = (e) => {
    e.stopPropagation();
  };

  return (
    <div className="niche-modal-overlay" onClick={handleOverlayClick}>
      <div className="niche-modal-card" onClick={handleCardClick}>
        <div className="niche-modal-header">
          <div className="niche-modal-title">Твоя ниша</div>
          <button
            type="button"
            className="niche-modal-close"
            aria-label="Закрыть"
            onClick={onClose}
          >
            ×
          </button>
        </div>
        <div className="niche-modal-body">
          <p>
            Это позиция на рынке, которую ты занимаешь. Она выражена тегами
            вверху экрана.
          </p>
          <p>
            Благодаря этим характеристикам мы можем подобрать наиболее прямых
            конкурентов, проанализировать их и помочь тебе выстроить новую
            стратегию.
          </p>
        </div>
      </div>
    </div>
  );
}

export default NicheHelpModal;
