import React, { useState } from "react";

function DateRangeModal({ initialFrom, initialTo, onApply, onClose }) {
  const [from, setFrom] = useState(initialFrom || "");
  const [to, setTo] = useState(initialTo || "");
  const [error, setError] = useState(null);

  const handleApply = () => {
    if (!from || !to || from > to) {
      setError("Выберите корректный диапазон");
      return;
    }
    setError(null);
    onApply({ from, to });
  };

  return (
    <div className="modal-backdrop">
      <div className="modal">
        <div className="modal-header">
          <h2 className="card-title">Выбор периода</h2>
          <button className="modal-close" type="button" onClick={onClose}>
            ×
          </button>
        </div>

        <div
          style={{
            display: "flex",
            flexDirection: "column",
            gap: 8,
            marginBottom: 12,
          }}
        >
          <label style={{ fontSize: 12 }}>
            От:
            <input
              type="date"
              className="input"
              value={from}
              onChange={(e) => setFrom(e.target.value)}
            />
          </label>
          <label style={{ fontSize: 12 }}>
            До:
            <input
              type="date"
              className="input"
              value={to}
              onChange={(e) => setTo(e.target.value)}
            />
          </label>
        </div>

        {error && <div className="error-text">{error}</div>}

        <button type="button" className="button" onClick={handleApply}>
          Выбрать
        </button>
      </div>
    </div>
  );
}

export default DateRangeModal;
