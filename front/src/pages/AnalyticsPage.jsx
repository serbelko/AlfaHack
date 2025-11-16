import React, { useState, useEffect } from "react";
import { useNavigate } from "react-router-dom";
import PeriodSelector from "../components/PeriodSelector";
import AnalyticsChart from "../components/AnalyticsChart";
import RecommendationCard from "../components/RecommendationCard";
import DateRangeModal from "../components/DateRangeModal";
import "./AnalyticsPage.css";
import { getCompetitors } from "../api/promotionApi";

// Если у тебя уже есть свой mockDataByPeriod — можешь использовать его вместо этого
const mockDataByPeriod = {
  month: {
    income: 700000,
    expenses: 350000,
    incomeData: [100000, 120000, 150000, 180000, 150000, 0, 0],
    expensesData: [50000, 60000, 70000, 80000, 90000, 0, 0],
    labels: ["Пн", "Вт", "Ср", "Чт", "Пт", "Сб", "Вс"],
  },
  year: {
    income: 8000000,
    expenses: 5200000,
    incomeData: [
      500000, 600000, 700000, 800000, 900000, 1000000, 900000, 800000, 700000,
      600000, 500000, 400000,
    ],
    expensesData: [
      300000, 320000, 340000, 360000, 380000, 400000, 420000, 440000, 460000,
      480000, 500000, 520000,
    ],
    labels: [
      "Янв",
      "Фев",
      "Мар",
      "Апр",
      "Май",
      "Июн",
      "Июл",
      "Авг",
      "Сен",
      "Окт",
      "Ноя",
      "Дек",
    ],
  },
  custom: {
    income: 0,
    expenses: 0,
    incomeData: [],
    expensesData: [],
    labels: [],
  },
};

function AnalyticsPage({ initialTab = "analytics" }) {
  const navigate = useNavigate();

  const [activeTab, setActiveTab] = useState(initialTab);
  const [period, setPeriod] = useState("month");
  const [customRange, setCustomRange] = useState({ from: null, to: null });
  const [showRangeModal, setShowRangeModal] = useState(false);

  const currentData = mockDataByPeriod[period] || mockDataByPeriod.month;

  // Состояния для продвижения
  const [city, setCity] = useState("Москва");
  const [niche, setNiche] = useState("Ногтевой сервис");
  const [priceSegment, setPriceSegment] = useState("До 5000₽");
  const [district, setDistrict] = useState("Сухаревская");

  const [competitors, setCompetitors] = useState([]);
  const [competitorsLoading, setCompetitorsLoading] = useState(false);
  const [competitorsError, setCompetitorsError] = useState(null);

  const handlePeriodChange = (value) => {
    if (value === "custom") {
      setShowRangeModal(true);
    } else {
      setPeriod(value);
      setCustomRange({ from: null, to: null });
    }
  };

  const handleApplyRange = ({ from, to }) => {
    setCustomRange({ from, to });
    setShowRangeModal(false);
    setPeriod("custom");
  };

  const formatCurrency = (value) => {
    return (
      new Intl.NumberFormat("ru-RU", {
        minimumFractionDigits: 2,
        maximumFractionDigits: 2,
      }).format(value) + "₽"
    );
  };

  // Загрузка конкурентов при переходе на вкладку "Продвижение"
  // или изменении фильтров
  useEffect(() => {
    if (activeTab !== "promotion") return;

    async function loadCompetitors() {
      setCompetitorsLoading(true);
      setCompetitorsError(null);

      try {
        const data = await getCompetitors({
          city,
          niche,
          price: priceSegment,
          district,
        });

        // поддерживаем оба варианта ответа:
        // либо массив, либо { competitors: [...] }
        const list = Array.isArray(data) ? data : data?.competitors || [];

        setCompetitors(list);
      } catch (err) {
        console.error("Ошибка загрузки конкурентов", err);
        if (err.status === 403) {
          setCompetitorsError("Сессия истекла. Войдите снова.");
        } else {
          setCompetitorsError("Не удалось загрузить конкурентов.");
        }
      } finally {
        setCompetitorsLoading(false);
      }
    }

    loadCompetitors();
  }, [activeTab, city, niche, priceSegment, district]);

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
          <h1 className="page-title">Альфа Помощник</h1>
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
            <PeriodSelector value={period} onChange={handlePeriodChange} />

            <div className="income-expenses-summary">
              <div className="summary-line">
                <span className="summary-label">Всего доходов </span>
                <span className="summary-value income">
                  {formatCurrency(currentData.income)}
                </span>
              </div>
              <div className="summary-line">
                <span className="summary-label">Всего расходов </span>
                <span className="summary-value expense">
                  {formatCurrency(currentData.expenses)}
                </span>
              </div>
            </div>

            <AnalyticsChart
              incomeData={currentData.incomeData}
              expensesData={currentData.expensesData}
              labels={currentData.labels}
            />
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
          {/* Карточка "Твоя ниша" */}
          <div className="analytics-card promotion-niche-card">
            <div className="card-title-row">
              <div className="card-title">Твоя ниша</div>
              <button
                type="button"
                className="niche-help-button"
                aria-label="Описание ниши"
              >
                ?
              </button>
            </div>

            <div className="niche-tags-row">
              <button
                type="button"
                className={`niche-tag ${
                  niche === "Ногтевой сервис" ? "niche-tag--active" : ""
                }`}
                onClick={() => setNiche("Ногтевой сервис")}
              >
                Ногтевой сервис
              </button>
              <button
                type="button"
                className={`niche-tag ${
                  city === "Москва" ? "niche-tag--active" : ""
                }`}
                onClick={() => setCity("Москва")}
              >
                Москва
              </button>
            </div>

            <div className="niche-tags-row">
              <button
                type="button"
                className={`niche-tag ${
                  priceSegment === "До 5000₽" ? "niche-tag--active" : ""
                }`}
                onClick={() => setPriceSegment("До 5000₽")}
              >
                До 5000₽
              </button>
              <button
                type="button"
                className={`niche-tag ${
                  district === "Сухаревская" ? "niche-tag--active" : ""
                }`}
                onClick={() => setDistrict("Сухаревская")}
              >
                Сухаревская
              </button>
            </div>
          </div>

          {/* Карточка "Основные конкуренты" */}
          <div className="analytics-card promotion-competitors-card">
            <div className="card-title">Основные конкуренты</div>

            {competitorsLoading && (
              <div className="card-subtitle">Загружаем конкурентов…</div>
            )}

            {competitorsError && !competitorsLoading && (
              <div className="error-text">{competitorsError}</div>
            )}

            {!competitorsLoading &&
              !competitorsError &&
              competitors.length === 0 && (
                <div className="card-subtitle">
                  По вашему запросу нет данных
                </div>
              )}

            {!competitorsLoading &&
              !competitorsError &&
              competitors.map((c) => (
                <div key={c.id || c.name} className="competitor-item">
                  <div className="competitor-avatar-placeholder" />
                  <div className="competitor-text">
                    <div className="competitor-label">Название</div>
                    <div className="competitor-name">{c.name}</div>
                    {c.profile && (
                      <div className="competitor-profile">{c.profile}</div>
                    )}
                    {c.description && !c.profile && (
                      <div className="competitor-profile">{c.description}</div>
                    )}
                  </div>
                </div>
              ))}
          </div>

          {/* Нижняя красная рекомендация под продвижение (можно потом вынести в компонент) */}
          <div className="promotion-tip-card">
            <div className="promotion-tip-text">
              Публикуйте больше сториз: клиентам больше доверяют студиям,
              которые готовы рассказывать о себе!
            </div>
            <button className="promotion-tip-button">Подробнее</button>
          </div>
        </div>
      )}
    </div>
  );
}

export default AnalyticsPage;
