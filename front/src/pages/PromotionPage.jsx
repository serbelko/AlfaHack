import React, { useEffect, useState, useCallback } from "react";
import { useNavigate } from "react-router-dom";
import "./AnalyticsPage.css";
import CompetitorCard from "../components/CompetitorCard";
import { getCompetitors } from "../api/promotionApi";

function PromotionPage() {
  const navigate = useNavigate();

  const [city, setCity] = useState("");
  const [niche, setNiche] = useState("");
  const [price, setPrice] = useState("");
  const [district, setDistrict] = useState("");
  const [competitors, setCompetitors] = useState([]);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState(null);

  const loadCompetitors = useCallback(
    async (paramsOverride) => {
      const params = paramsOverride || { city, niche, price, district };
      setIsLoading(true);
      setError(null);
      try {
        const data = await getCompetitors(params);
        if (Array.isArray(data)) {
          setCompetitors(data);
        } else if (data && Array.isArray(data.competitors)) {
          setCompetitors(data.competitors);
        } else {
          setCompetitors([]);
        }
      } catch (e) {
        setError(e.message || "Ошибка загрузки данных");
        setCompetitors([]);
      } finally {
        setIsLoading(false);
      }
    },
    [city, niche, price, district]
  );

  useEffect(() => {
    loadCompetitors();
  }, [loadCompetitors]);

  const handleSubmit = (e) => {
    e.preventDefault();
    loadCompetitors();
  };

  const handleReset = () => {
    setCity("");
    setNiche("");
    setPrice("");
    setDistrict("");
    loadCompetitors({ city: "", niche: "", price: "", district: "" });
  };

  return (
    <div className="analytics-page">
      <header className="analytics-header">
        <div className="header-left">
          <button
            type="button"
            className="back-button"
            onClick={() => navigate(-1)}
          >
            <span>Назад</span>
          </button>
          <div className="header-title-block">
            <h1 className="header-title">Продвижение</h1>
            <div className="header-subtitle">
              Анализ конкурентов и подсказки по промо
            </div>
          </div>
        </div>
        <div className="header-tabs">
          <button
            type="button"
            className="header-tab"
            onClick={() => navigate("/analytics")}
          >
            Аналитика
          </button>
          <button type="button" className="header-tab header-tab-active">
            Продвижение
          </button>
        </div>
      </header>

      <div className="analytics-content">
        <form className="analytics-filters" onSubmit={handleSubmit}>
          <div className="filter-row">
            <div className="filter-field">
              <label className="filter-label">Город</label>
              <input
                className="filter-input"
                type="text"
                value={city}
                onChange={(e) => setCity(e.target.value)}
                placeholder="Например, Казань"
              />
            </div>
            <div className="filter-field">
              <label className="filter-label">Район</label>
              <input
                className="filter-input"
                type="text"
                value={district}
                onChange={(e) => setDistrict(e.target.value)}
                placeholder="Центр, Спальный и т.д."
              />
            </div>
          </div>
          <div className="filter-row">
            <div className="filter-field">
              <label className="filter-label">Ниша</label>
              <input
                className="filter-input"
                type="text"
                value={niche}
                onChange={(e) => setNiche(e.target.value)}
                placeholder="Кофейня to-go, барбершоп..."
              />
            </div>
            <div className="filter-field">
              <label className="filter-label">Чек/цена</label>
              <input
                className="filter-input"
                type="text"
                value={price}
                onChange={(e) => setPrice(e.target.value)}
                placeholder="Средний чек или диапазон"
              />
            </div>
          </div>
          <div className="filter-actions">
            <button type="submit" className="primary-button">
              Найти конкурентов
            </button>
            <button
              type="button"
              className="secondary-button"
              onClick={handleReset}
            >
              Сбросить фильтры
            </button>
          </div>
        </form>

        <section className="analytics-section">
          <h2 className="section-title">Конкуренты поблизости</h2>
          {isLoading && (
            <div className="empty-state">Загружаем список конкурентов...</div>
          )}
          {error && !isLoading && <div className="empty-state">{error}</div>}
          {!isLoading && !error && competitors.length === 0 && (
            <div className="empty-state">
              Мы не нашли конкурентов по текущим фильтрам. Попробуйте изменить
              параметры поиска.
            </div>
          )}
          {!isLoading && !error && competitors.length > 0 && (
            <div className="competitors-list">
              {competitors.map((competitor) => (
                <CompetitorCard
                  key={competitor.id || competitor.name}
                  competitor={competitor}
                />
              ))}
            </div>
          )}
        </section>

        <section className="analytics-section">
          <h2 className="section-title">Подсказка по продвижению</h2>
          <div className="promotion-tip-card">
            <div className="promotion-tip-text">
              Публикуйте больше сториз и коротких видео из точки: клиентам проще
              доверять студиям и кофейням, которые регулярно показывают живой
              процесс и команду.
            </div>
            <button
              type="button"
              className="promotion-tip-button"
              onClick={() => navigate("/analytics/recommendation")}
            >
              Подробнее
            </button>
          </div>
        </section>
      </div>
    </div>
  );
}

export default PromotionPage;
