import React from "react";
import { useNavigate, useParams } from "react-router-dom";
import { useEffect, useState } from 'react';
import { getCompetitorById } from '../api/promotionApi';

function CompetitorDetailPage() {
  const { id } = useParams();
  const navigate = useNavigate();

  const [competitor, setCompetitor] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    async function load() {
      setLoading(true);
      setError(null);
      try {
        const data = await getCompetitorById(id);
        setCompetitor(data);
      } catch (err) {
        console.error(err);
        setError('Не удалось загрузить данные конкурента.');
      } finally {
        setLoading(false);
      }
    }

    load();
  }, [id]);

  return (
    <div className="modal-page">
      <header className="modal-header">
        <h1 className="page-title">Конкурент</h1>
        <button
          type="button"
          className="icon-button"
          onClick={() => navigate(-1)}
          aria-label="Закрыть"
        >
          ×
        </button>
      </header>

      <div className="card">
        {loading && <div className="card-subtitle">Загрузка...</div>}
        {error && !loading && <div className="error-text">{error}</div>}
        {competitor && !loading && !error && (
          <>
            <div className="competitor-image-placeholder" />
            <div className="card-title">{competitor.name}</div>
            <div className="card-subtitle">{competitor.subtitle}</div>
            <p style={{ marginTop: 12, fontSize: 14, lineHeight: 1.4 }}>
              {competitor.description}
            </p>
          </>
        )}
      </div>
    </div>
  );
}

export default CompetitorDetailPage;

