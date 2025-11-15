import React from "react";

function WarningCard({ title, text }) {
  return (
    <div
      className="card"
      style={{
        backgroundColor: "#fee2e2",
        border: "1px solid #fecaca",
      }}
    >
      <div className="card-title" style={{ color: "#b91c1c" }}>
        {title}
      </div>
      <div className="card-subtitle" style={{ color: "#7f1d1d" }}>
        {text}
      </div>
    </div>
  );
}

export default WarningCard;
