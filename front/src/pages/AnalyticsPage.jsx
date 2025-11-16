import React, { useState, useEffect } from "react";
import { useNavigate } from "react-router-dom";
import PeriodSelector from "../components/PeriodSelector";
import AnalyticsChart from "../components/AnalyticsChart";
import RecommendationCard from "../components/RecommendationCard";
import DateRangeModal from "../components/DateRangeModal";
import NicheHelpModal from "../components/NicheHelpModal";
import "./AnalyticsPage.css";
import { getCompetitors } from "../api/promotionApi";
import { getAnalyticsFromHistory } from "../api/analyticsApi";
import nailsImage from "../assets/competitors/nails.png";
import spaImage from "../assets/competitors/spa.png";
import massageImage from "../assets/competitors/massage.png";
import headerAvatar from "../assets/header/avatar.png";
import { getRecommendationSegment } from "../api/aiApi";

const mockDataByPeriod = {
  month: {
    income: 700000,
    expenses: 350000,
    incomeData: [100000, 120000, 150000, 180000, 150000, 0, 0],
    expensesData: [50000, 60000, 70000, 80000, 90000, 0, 0],
    labels: ["Пн", "Вт", "Ср", "Чт", "Пт", "Сб", "Вс"],
  },
  year: {
    income: 8200000,
    expenses: 5100000,
    incomeData: [
      500000, 600000, 700000, 800000, 900000, 1000000, 1100000, 900000, 800000,
      700000, 600000, 500000,
    ],
    expensesData: [
      300000, 350000, 400000, 450000, 500000, 550000, 600000, 500000, 450000,
      400000, 350000, 300000,
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

const competitorStubData = [
  {
    id: 1,
    name: "Имидж-лаборатория",
    profile:
      "Аппаратный, комбинированный маникюр и педикюр, модный дизайн, спа-уход",
    image: nailsImage,
  },
  {
    id: 2,
    name: "Спа-центр",
    profile: "Подарочные сертификаты, которые приятно дарить",
    image: spaImage,
  },
  {
    id: 3,
    name: "Сеть салонов красоты",
    profile: "Полный спектр услуг по уходу за собой",
    image: massageImage,
  },
];

function formatCurrency(value) {
  return new Intl.NumberFormat("ru-RU", {
    style: "currency",
    currency: "RUB",
    maximumFractionDigits: 0,
  }).format(value);
}

function AnalyticsPage({ initialTab = "analytics" }) {
  const navigate = useNavigate();
  const [recommendationSegment, setRecommendationSegment] = useState(null);

  const [activeTab, setActiveTab] = useState(initialTab);
  const [period, setPeriod] = useState("month");
  const [customRange, setCustomRange] = useState({ from: null, to: null });
  const [showRangeModal, setShowRangeModal] = useState(false);

  const [city, setCity] = useState("Москва");
  const [niche, setNiche] = useState("Ногтевой сервис");
  const [priceSegment, setPriceSegment] = useState("До 5000₽");
  const [district, setDistrict] = useState("Сухаревская");

  const [competitors, setCompetitors] = useState(competitorStubData);
  const [competitorsLoading, setCompetitorsLoading] = useState(false);
  const [competitorsError, setCompetitorsError] = useState(null);

  const [showNicheHelp, setShowNicheHelp] = useState(false);

  const [analyticsData, setAnalyticsData] = useState(null);
  const [analyticsLoading, setAnalyticsLoading] = useState(false);
  const [analyticsError, setAnalyticsError] = useState(null);

  const baseData = mockDataByPeriod[period] || mockDataByPeriod.month;
  const currentData = analyticsData || baseData;

  const handlePeriodChange = (value) => {
    if (value === "custom") {
      setShowRangeModal(true);
    } else {
      setPeriod(value);
      setCustomRange({ from: null, to: null });
    }
  };
  useEffect(() => {
    let isCancelled = false;

    async function loadRecommendation() {
      try {
        const segment = await getRecommendationSegment({
          city,
          niche: "Кофейня to-go", // можно завязать на реальные поля, если есть
          priceSegment,
          district,
        });

        if (!isCancelled) {
          setRecommendationSegment(segment);
        }
      } catch (err) {
        console.error("Failed to load AI recommendation", err);
        if (!isCancelled) {
          // Фоллбек: просто оставляем null - фронт покажет шаблон
          setRecommendationSegment(null);
        }
      }
    }

    loadRecommendation();

    return () => {
      isCancelled = true;
    };
  }, [city, priceSegment, district]);

  const handleApplyRange = ({ from, to }) => {
    setCustomRange({ from, to });
    setPeriod("custom");
    setShowRangeModal(false);
  };

  useEffect(() => {
    if (activeTab !== "analytics") return;
    let cancelled = false;

    async function loadAnalytics() {
      setAnalyticsLoading(true);
      setAnalyticsError(null);
      try {
        const params =
          period === "custom"
            ? { period, from: customRange.from, to: customRange.to }
            : { period };
        const data = await getAnalyticsFromHistory(params);
        if (!cancelled) {
          if (data.incomeData.length === 0 && data.expensesData.length === 0) {
            setAnalyticsData(null);
          } else {
            setAnalyticsData(data);
          }
        }
      } catch (e) {
        if (!cancelled) {
          setAnalyticsData(null);
          setAnalyticsError(e.status || "error");
        }
      } finally {
        if (!cancelled) {
          setAnalyticsLoading(false);
        }
      }
    }

    loadAnalytics();

    return () => {
      cancelled = true;
    };
  }, [activeTab, period, customRange.from, customRange.to]);

  useEffect(() => {
    if (activeTab !== "promotion") {
      return;
    }

    let isCancelled = false;

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

        const list = Array.isArray(data)
          ? data
          : Array.isArray(data?.competitors)
          ? data.competitors
          : [];

        if (!isCancelled) {
          if (list.length > 0) {
            setCompetitors(list);
          } else {
            setCompetitors(competitorStubData);
          }
        }
      } catch {
        if (!isCancelled) {
          setCompetitors(competitorStubData);
          setCompetitorsError(null);
        }
      } finally {
        if (!isCancelled) {
          setCompetitorsLoading(false);
        }
      }
    }

    loadCompetitors();

    return () => {
      isCancelled = true;
    };
  }, [activeTab, city, niche, priceSegment, district]);

  return (
    <div className="analytics-page">
      <header className="analytics-header">
        <div className="header-top">
          <div className="header-left">
            <button
              type="button"
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
          <div className="header-avatar">
            <img src={headerAvatar} alt="Профиль" />
          </div>
        </div>

        <div className="header-tabs">
          <button
            type="button"
            className={`header-tab ${
              activeTab === "analytics" ? "header-tab-active" : ""
            }`}
            onClick={() => setActiveTab("analytics")}
          >
            Аналитика
          </button>
          <button
            type="button"
            className={`header-tab ${
              activeTab === "promotion" ? "header-tab-active" : ""
            }`}
            onClick={() => setActiveTab("promotion")}
          >
            Продвижение
          </button>
        </div>
      </header>

      {activeTab === "analytics" && (
        <div className="analytics-content">
          <div className="analytics-card">
            <PeriodSelector value={period} onChange={handlePeriodChange} />
            <div className="income-expenses-summary">
              <div className="summary-line">
                <span className="summary-label">Всего доходов</span>
                <span className="summary-value income">
                  {formatCurrency(currentData.income || 0)}
                </span>
              </div>
              <div className="summary-line">
                <span className="summary-label">Всего расходов</span>
                <span className="summary-value expense">
                  {formatCurrency(currentData.expenses || 0)}
                </span>
              </div>
            </div>
            {analyticsLoading && (
              <div className="analytics-loading">Загружаем данные…</div>
            )}
            {!analyticsLoading && analyticsError && (
              <div className="analytics-error">
                Не удалось загрузить данные, показана заглушка
              </div>
            )}
            <AnalyticsChart
              incomeData={currentData.incomeData}
              expensesData={currentData.expensesData}
              labels={currentData.labels}
            />
          </div>

          <RecommendationCard segment={recommendationSegment} />
        </div>
      )}

      {activeTab === "promotion" && (
        <div className="promotion-content">
          <div className="analytics-card promotion-niche-card">
            <div className="card-title-row">
              <div className="card-title">Твоя ниша</div>
              <button
                type="button"
                className="niche-help-button"
                aria-label="Описание ниши"
                onClick={() => setShowNicheHelp(true)}
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

          <div className="analytics-card promotion-competitors-card">
            <div className="card-title">Основные конкуренты</div>

            {competitorsLoading && (
              <div className="card-subtitle">Загружаем конкурентов…</div>
            )}

            {!competitorsLoading &&
              !competitorsError &&
              competitors.length === 0 && (
                <div className="card-subtitle">
                  По вашему запросу нет данных
                </div>
              )}

            {!competitorsLoading && competitorsError && (
              <div className="error-text">{competitorsError}</div>
            )}

            {!competitorsLoading &&
              !competitorsError &&
              competitors.map((c) => (
                <div key={c.id || c.name} className="competitor-item">
                  <div className="competitor-avatar-placeholder">
                    {c.image && (
                      <img
                        src={c.image}
                        alt={c.name}
                        className="competitor-avatar-image"
                      />
                    )}
                  </div>
                  <div className="competitor-text">
                    <div className="competitor-label">Название</div>
                    <div className="competitor-name">{c.name}</div>
                    {c.profile && (
                      <div className="competitor-profile">{c.profile}</div>
                    )}
                    {c.description && (
                      <div className="competitor-profile">{c.description}</div>
                    )}
                  </div>
                </div>
              ))}
          </div>

          <div className="promotion-tip-card">
            <div className="promotion-tip-text">
              Публикуйте больше сториз: клиентам больше доверяют студиям,
              которые готовы рассказывать о себе!
            </div>
            <button
              type="button"
              className="promotion-tip-button"
              onClick={() => navigate("/analytics/recommendation")}
            >
              Подробнее
            </button>
          </div>
        </div>
      )}

      {showRangeModal && (
        <DateRangeModal
          initialFrom={customRange.from}
          initialTo={customRange.to}
          onApply={handleApplyRange}
          onClose={() => setShowRangeModal(false)}
        />
      )}

      {showNicheHelp && (
        <NicheHelpModal onClose={() => setShowNicheHelp(false)} />
      )}
    </div>
  );
}

export default AnalyticsPage;
