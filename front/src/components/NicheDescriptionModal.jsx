import React from "react";

function NicheDescriptionModal({ text, onClose }) {
  return (
    <div className="modal-backdrop">
      <div className="modal">
        <div className="modal-header">
          <h2 className="card-title">Описание ниши</h2>
          <button className="modal-close" type="button" onClick={onClose}>
            ×
          </button>
        </div>
        <p style={{ fontSize: 14, lineHeight: 1.4 }}>{text}</p>
      </div>
    </div>
  );
}

export default NicheDescriptionModal;
