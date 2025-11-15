import React, { useState } from "react";
import { useNavigate } from "react-router-dom";
import PeriodSelector from "../components/PeriodSelector";
import AnalyticsChart from "../components/AnalyticsChart";
import RecommendationCard from "../components/RecommendationCard";
import DateRangeModal from "../components/DateRangeModal";
import CompetitorCard from "../components/CompetitorCard";
import NicheDescriptionModal from "../components/NicheDescriptionModal";
import "./AnalyticsPage.css";

const mockAnalytics = {
  income: [100000, 120000, 90000],
  expenses: [70000, 95000, 110000],
  dates: ["2024-05-01", "2024-06-01", "2024-07-01"],
};

const mockCompetitors = [
  {
    id: 1,
    name: "Название",
    subtitle: "Имидж-лаборатория",
    description:
      "Аппаратный, комбинированный маникюр и педикюр, модный дизайн, спа-уход",
  },
  {
    id: 2,
    name: "Название",
    subtitle: "Спа-центр",
    description: "Подарочные сертификаты, которые приятно дарить",
  },
  {
    id: 3,
    name: "Название",
    subtitle: "Сеть салонов красоты",
    description: "Стрижка за 499 рублей. Ждём вас!",
  },
];

const nicheDescriptionMock =
  "Небольшие кофейни с фокусом на to-go и быстрый сервис. Основной трафик — офисные сотрудники и жители рядом. Важны стабильное качество, скорость обслуживания и простые промо-механики.";

function AnalyticsPage({ initialTab = "analytics" }) {
  const navigate = useNavigate();
  const [activeTab, setActiveTab] = useState(initialTab);
  const [period, setPeriod] = useState("month");
  const [customRange, setCustomRange] = useState({ from: "", to: "" });
  const [showRangeModal, setShowRangeModal] = useState(false);
  const [showNicheModal, setShowNicheModal] = useState(false);

  const hasData = mockAnalytics.income.length > 0;

  const handlePeriodChange = (value) => {
    setPeriod(value);
    if (value === "custom") {
      setShowRangeModal(true);
    } else {
      setCustomRange({ from: "", to: "" });
    }
  };

  const handleApplyRange = ({ from, to }) => {
    setCustomRange({ from, to });
    setShowRangeModal(false);
    setPeriod("custom");
  };

  return (
    <div className="analytics-page">
      <header className="analytics-header">
        <div className="header-left">
          <button
            className="back-button"
            onClick={() => navigate("/")}
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
          <h1 className="page-header-title">Альфа Помощник</h1>
        </div>
        <div className="assistant-avatar"></div>
      </header>

      <div className="tab-selector">
        <button
          className={`tab-button ${activeTab === "analytics" ? "active" : ""}`}
          onClick={() => setActiveTab("analytics")}
        >
          Аналитика
        </button>
        <button
          className={`tab-button ${activeTab === "promotion" ? "active" : ""}`}
          onClick={() => setActiveTab("promotion")}
        >
          Продвижение
        </button>
      </div>

      {activeTab === "analytics" && (
        <div className="analytics-content">
          <div className="analytics-card">
            <div className="analytics-card-title">Период</div>
            <PeriodSelector value={period} onChange={handlePeriodChange} />
            {period === "custom" && customRange.from && customRange.to && (
              <div className="custom-period-text">
                Выбран период: {customRange.from} — {customRange.to}
              </div>
            )}
          </div>

          <div className="analytics-card">
            <div className="analytics-card-title">Доходы и расходы</div>
            <AnalyticsChart hasData={hasData} />
          </div>

          <RecommendationCard />

          {showRangeModal && (
            <DateRangeModal
              initialFrom={customRange.from}
              initialTo={customRange.to}
              onApply={handleApplyRange}
              onClose={() => setShowRangeModal(false)}
            />
          )}
        </div>
      )}

      {activeTab === "promotion" && (
        <div className="promotion-content">
          <div className="niche-card">
            <div className="niche-header">
              <span className="niche-title">Твоя ниша</span>
              <button
                className="help-button"
                onClick={() => setShowNicheModal(true)}
                aria-label="Помощь"
              >
                ?
              </button>
            </div>
            <div className="niche-tags">
              <span className="niche-tag">Ногтевой сервис</span>
              <span className="niche-tag">Москва</span>
              <span className="niche-tag">До 5000₽</span>
              <span className="niche-tag">Сухаревская</span>
            </div>
          </div>

          <div className="competitors-section">
            <div className="competitors-title">Основные конкуренты</div>
            <div className="competitors-list">
              {mockCompetitors.map((competitor, index) => (
                <React.Fragment key={competitor.id}>
                  <CompetitorCard competitor={competitor} />
                  {index < mockCompetitors.length - 1 && (
                    <div className="competitor-divider"></div>
                  )}
                </React.Fragment>
              ))}
            </div>
          </div>

          <div className="recommendation-promo">
            <div className="promo-avatar"></div>
            <div className="promo-content">
              <div className="promo-title">Твоя рекомендация</div>
              <div className="promo-text">
                Публикуйте больше сториз. клиентам больше доверяют студиям,
                которые готовы рассказывать о себе!
              </div>
              <button className="promo-button">
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

          {showNicheModal && (
            <NicheDescriptionModal
              text={nicheDescriptionMock}
              onClose={() => setShowNicheModal(false)}
            />
          )}
        </div>
      )}
    </div>
  );
}

export default AnalyticsPage;
