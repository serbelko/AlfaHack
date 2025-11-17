import React from "react";
import { useNavigate, useLocation } from "react-router-dom";
import "./RecommendationDetailsPage.css";
import recAvatar from "../assets/recommendation/recommend-avatar.png";

function RecommendationDetailsPage() {
  const navigate = useNavigate();
  const location = useLocation();

  const segment = location.state?.segment || null;

  const handleBack = () => {
    navigate(-1);
  };

  const hasSegment = segment === "FIN" || segment === "MRKT";

  return (
    <div className="reco-page">
      <header className="reco-header">
        <button
          type="button"
          className="reco-back-button"
          onClick={handleBack}
          aria-label="Назад"
        >
          <svg
            width="8"
            height="14"
            viewBox="0 0 8 14"
            fill="none"
            xmlns="http://www.w3.org/2000/svg"
          >
            <path
              d="M6.65674 12.3137L0.999885 6.65685L6.65674 0.999997"
              stroke="black"
              strokeWidth="2"
              strokeLinecap="round"
              strokeLinejoin="round"
            />
          </svg>
        </button>
        <h1 className="reco-header-title">Альфа Помощник</h1>
      </header>

      <main className="reco-content">
        <section className="reco-card">
          <div className="reco-card-header">
            <div className="reco-card-avatar">
              <img
                src={recAvatar}
                alt="Рекомендация"
                className="reco-card-avatar-image"
              />
            </div>
            <div className="reco-card-header-text">
              <div className="reco-card-label">Твоя рекомендация</div>
              <div className="reco-card-main-title">
                {hasSegment
                  ? segment === "FIN"
                    ? "Сейчас важнее навести порядок в деньгах"
                    : "Сейчас важнее поработать с клиентами и маркетингом"
                  : "Обрати внимание на эквайринг"}
              </div>
            </div>
          </div>

          {hasSegment ? (
            segment === "FIN" ? (
              <>
                <p className="reco-intro">
                  По данным помощника, у тебя сейчас более узкое место в
                  финансовых потоках, а не в маркетинге.
                </p>

                <div className="reco-block">
                  <div className="reco-block-title">Почему это важно</div>
                  <ul className="reco-list">
                    <li className="reco-list-item">
                      Непрозрачный учёт мешает понимать реальную прибыль и
                      контролировать кассовые разрывы.
                    </li>
                    <li className="reco-list-item">
                      Без нормальной структуры расходов трудно принимать
                      решения: нанимать людей, расширять меню, менять цены.
                    </li>
                    <li className="reco-list-item">
                      Чёткий учёт помогает переживать просадки по выручке без
                      паники и долгов.
                    </li>
                  </ul>
                </div>

                <div className="reco-block">
                  <div className="reco-block-title">
                    Что можно сделать сейчас
                  </div>
                  <ul className="reco-list">
                    <li className="reco-list-item">
                      Выделить отдельный счёт для бизнеса и проводить все
                      операционные платежи только через него.
                    </li>
                    <li className="reco-list-item">
                      Завести простую структуру категорий расходов и доходов и
                      вносить операции каждый день.
                    </li>
                    <li className="reco-list-item">
                      Настроить регулярный контроль: раз в неделю смотреть
                      суммарную выручку, расходы и свободный остаток.
                    </li>
                  </ul>
                </div>
              </>
            ) : (
              <>
                <p className="reco-intro">
                  По данным помощника, сейчас больше потенциала в работе с
                  клиентами и маркетингом, чем во внутренней оптимизации
                  расходов.
                </p>

                <div className="reco-block">
                  <div className="reco-block-title">Почему это важно</div>
                  <ul className="reco-list">
                    <li className="reco-list-item">
                      При стабильных расходах рост выручки сильнее всего зависит
                      от потока и возвратности клиентов.
                    </li>
                    <li className="reco-list-item">
                      Те же ресурсы (аренда, персонал) могут приносить больше
                      при лучшей загрузке.
                    </li>
                    <li className="reco-list-item">
                      Сильный маркетинг позволяет переживать сезонные просадки
                      за счёт повторных визитов и рекомендаций.
                    </li>
                  </ul>
                </div>

                <div className="reco-block">
                  <div className="reco-block-title">
                    Что можно сделать сейчас
                  </div>
                  <ul className="reco-list">
                    <li className="reco-list-item">
                      Сформулировать простое предложение: кому ты помогаешь и
                      чем отличаешься от соседей.
                    </li>
                    <li className="reco-list-item">
                      Настроить базовый сценарий возврата клиентов: напоминания,
                      бонусы за повторный визит.
                    </li>
                    <li className="reco-list-item">
                      Посмотреть, какие каналы реально приводят людей сейчас, и
                      усилить именно их, а не распыляться.
                    </li>
                  </ul>
                </div>
              </>
            )
          ) : (
            <>
              {/* Фоллбек — твой исходный шаблон, если AI/бэк не ответили */}
              <p className="reco-intro">
                Позже здесь будут отображаться персональные рекомендации с
                бэкенда. Сейчас это заглушка, чтобы можно было протестировать
                навигацию и экран рекомендаций.
              </p>

              <div className="reco-block">
                <div className="reco-block-title">Почему это важно</div>
                <ul className="reco-list">
                  <li className="reco-list-item">
                    Клиентам удобнее оплачивать картой сразу после услуги, это
                    повышает конверсию в оплату.
                  </li>
                  <li className="reco-list-item">
                    Безналичные платежи позволяют точнее считать выручку по дням
                    и неделям в аналитике.
                  </li>
                  <li className="reco-list-item">
                    Прозрачный денежный поток помогает планировать аренду,
                    закупки и зарплаты без кассовых разрывов.
                  </li>
                </ul>
              </div>

              <div className="reco-block">
                <div className="reco-block-title">Что можно сделать сейчас</div>
                <ul className="reco-list">
                  <li className="reco-list-item">
                    Подключить эквайринг и добавить оплату картой во все
                    основные сценарии работы с клиентом.
                  </li>
                  <li className="reco-list-item">
                    Отслеживать долю оплат по карте в разделе аналитики и
                    смотреть, как она меняется по месяцам.
                  </li>
                  <li className="reco-list-item">
                    Использовать безнал как повод для акций и программ
                    лояльности, чтобы увеличить повторные визиты.
                  </li>
                </ul>
              </div>
            </>
          )}

          <button
            type="button"
            className="reco-primary-button"
            onClick={handleBack}
          >
            Понятно, вернуться
          </button>
        </section>
      </main>
    </div>
  );
}

export default RecommendationDetailsPage;
