import React from "react";
import { useNavigate } from "react-router-dom";
import "./AnalyticsPage.css";

function ContactPage() {
  const navigate = useNavigate();

  return (
    <div className="analytics-page">
      <header className="analytics-header">
        <div className="header-left">
          <button
            type="button"
            className="back-button"
            onClick={() => navigate(-1)}
            aria-label="Назад"
          >
            <svg width="8" height="14" viewBox="0 0 8 14" fill="none">
              <path
                d="M6.65674 12.3137L0.999885 6.65685L6.65674 0.999997"
                stroke="black"
                strokeWidth="2"
                strokeLinecap="round"
                strokeLinejoin="round"
              />
            </svg>
          </button>
          <h1 className="page-title">Связь</h1>
        </div>
      </header>

      <div className="analytics-content">
        <div className="analytics-card">
          <div className="card-title">Связаться с нами</div>
          <div className="card-subtitle">
            Здесь будет экран поддержки или чат. Сейчас это заглушка, чтобы
            нижнее меню не перекидывало на авторизацию.
          </div>
        </div>
      </div>
    </div>
  );
}

export default ContactPage;
