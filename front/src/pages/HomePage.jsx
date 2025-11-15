import React, { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import "./HomePage.css";
import { getAllAmounts } from "../api/amountApi";

// форматирование денег под "русский" формат
function formatAmountRu(value) {
  if (typeof value !== "number" || Number.isNaN(value)) {
    return "0,00";
  }
  return value.toLocaleString("ru-RU", {
    minimumFractionDigits: 2,
    maximumFractionDigits: 2,
  });
}

function HomePage() {
  const navigate = useNavigate();

  const [accounts, setAccounts] = useState([]);

  useEffect(() => {
    async function loadAccounts() {
      try {
        const data = await getAllAmounts();
        // ТЗ: { amounts: { { "count": 123, "name": "string" } }, limit_data: int }
        const amounts = data?.amounts || [];
        setAccounts(amounts);
      } catch (err) {
        console.error("Ошибка загрузки счетов", err);
        setAccounts([]);
      }
    }

    loadAccounts();
  }, []);

  // суммарный остаток по всем счетам
  const totalBalance = accounts.reduce((sum, acc) => sum + (acc.count || 0), 0);
  const totalFormatted = formatAmountRu(totalBalance);
  const [totalWhole, totalDecimal = "00"] = totalFormatted.split(",");

  return (
    <div className="home-page">
      <header className="home-header">
        <div className="logo-circle">
          <span>А</span>
        </div>

        <div className="business-selector">
          <span>ООО «Город Нагатино»</span>
          <svg width="14" height="15" viewBox="0 0 14 15" fill="none">
            <path
              d="M1 5.65685L6.65685 11.3137L12.3137 5.65685"
              stroke="black"
              strokeWidth="2"
              strokeLinecap="round"
              strokeLinejoin="round"
            />
          </svg>
        </div>

        <button className="icon-button calendar-icon" aria-label="Календарь">
          <svg width="21" height="23" viewBox="0 0 21 23" fill="none">
            <path
              d="M1 3.12612H19.9932V18.474C19.9932 20.1309 18.65 21.474 16.9932 21.474H4C2.34315 21.474 1 20.1309 1 18.474V3.12612Z"
              stroke="black"
              strokeWidth="2"
            />
            <path
              d="M0.993164 7.44305H19.9932"
              stroke="black"
              strokeWidth="2"
            />
            <rect
              x="4.49658"
              y="11.5"
              width="2"
              height="2"
              rx="0.55"
              fill="black"
            />
            <rect
              x="9.49658"
              y="11.5"
              width="2"
              height="2"
              rx="0.55"
              fill="black"
            />
            <rect
              x="14.4966"
              y="11.5"
              width="2"
              height="2"
              rx="0.55"
              fill="black"
            />
            <rect
              x="4.49658"
              y="16.5"
              width="2"
              height="2"
              rx="0.55"
              fill="black"
            />
            <rect
              x="9.49658"
              y="16.5"
              width="2"
              height="2"
              rx="0.55"
              fill="black"
            />
            <rect
              x="14.4966"
              y="16.5"
              width="2"
              height="2"
              rx="0.55"
              fill="black"
            />
            <path
              d="M5.74487 2.4642V0.0133057"
              stroke="black"
              strokeWidth="2"
            />
            <path d="M15.2415 2.45089V0" stroke="black" strokeWidth="2" />
          </svg>
        </button>

        <button className="icon-button bell-icon" aria-label="Уведомления">
          <svg width="30" height="30" viewBox="0 0 30 30" fill="none">
            <path
              d="M10.253 7.42462C13.5725 4.10517 18.9544 4.10516 22.2739 7.42462C25.5933 10.7441 25.5933 16.126 22.2739 19.4454L19.3523 22.367C19.1143 22.605 18.9395 22.8987 18.8438 23.2214L17.7972 26.7505L2.94794 11.9013L6.47705 10.8547C6.79978 10.759 7.09349 10.5842 7.33152 10.3461L10.253 7.42462Z"
              fill="black"
            />
            <path
              d="M10.9794 22.3859C10.5228 22.8424 9.89186 23.0871 9.22522 23.0661C8.55859 23.0451 7.91091 22.7601 7.42467 22.2739C6.93843 21.7876 6.65346 21.1399 6.63244 20.4733C6.61143 19.8067 6.85609 19.1757 7.31261 18.7192L9.14599 20.5525L10.9794 22.3859Z"
              fill="black"
            />
          </svg>
        </button>
      </header>

      <div className="balance-cards">
        <div className="balance-card">
          <div className="balance-content">
            <div className="balance-label">Доступный остаток</div>
            <div className="balance-amount">
              <span className="amount-whole">
                {totalWhole?.replace(/\u00A0/g, " ")}
              </span>
              <span className="amount-decimal">,{totalDecimal} ₽</span>
            </div>
            <div className="balance-subtitle">
              на {accounts.length} рублёвых счетах
            </div>
          </div>
          <svg
            className="chevron-icon"
            width="8"
            height="14"
            viewBox="0 0 8 14"
            fill="none"
          >
            <path
              d="M1 12.3137L6.65685 6.65685L0.999999 1"
              stroke="#A3A3A3"
              strokeWidth="2"
              strokeLinecap="round"
              strokeLinejoin="round"
            />
          </svg>
        </div>

        <div className="balance-card deposits">
          <div className="balance-content">
            <div className="balance-label">Депозиты</div>
            <div className="balance-amount">
              <span className="amount-whole">700 500</span>
              <span className="amount-decimal">,00 ₽</span>
            </div>
            <div className="balance-subtitle">на 2 рублёвых счетах</div>
          </div>
        </div>
      </div>

      <div className="assistant-card" onClick={() => navigate("/analytics")}>
        <div className="assistant-header">
          <div className="assistant-title-group">
            <div className="assistant-avatar"></div>
            <div className="assistant-name">Альфа Помощник</div>
          </div>
          <svg
            className="chevron-icon-white"
            width="8"
            height="14"
            viewBox="0 0 8 14"
            fill="none"
          >
            <path
              d="M1 12.3137L6.65685 6.65685L0.999999 0.999997"
              stroke="white"
              strokeWidth="2"
              strokeLinecap="round"
              strokeLinejoin="round"
            />
          </svg>
        </div>
        <div className="assistant-message">
          Подготовил анализ твоих финансов! Хочешь посмотреть?
        </div>
      </div>

      <div className="accounts-list">
        {accounts.map((account, index) => {
          const formatted = formatAmountRu(account.count || 0);
          const [whole, decimal = "00"] = formatted.split(",");

          return (
            <div key={account.name || index} className="account-item">
              <div className="currency-icon">
                <span>₽</span>
              </div>
              <div className="account-details">
                <div className="account-amount">
                  <span className="amount-bold">
                    {whole?.replace(/\u00A0/g, " ")}
                  </span>
                  <span>,{decimal}</span>
                </div>
                <div
                  className={`account-name ${
                    account.warning ? "has-warning" : ""
                  }`}
                >
                  <span className="account-number">{account.name}</span>
                  {account.warning && (
                    <>
                      {" "}
                      <span className="warning-text">{account.warning}</span>
                    </>
                  )}
                </div>
              </div>
            </div>
          );
        })}
      </div>

      <div className="all-accounts-link" onClick={() => navigate("/accounts")}>
        <div className="all-accounts-content">
          <span>Все счета и карты</span>
          <svg
            className="chevron-icon"
            width="8"
            height="14"
            viewBox="0 0 8 14"
            fill="none"
          >
            <path
              d="M1 12.3137L6.65685 6.65687L0.999999 1.00001"
              stroke="#A3A3A3"
              strokeWidth="2"
              strokeLinecap="round"
              strokeLinejoin="round"
            />
          </svg>
        </div>
      </div>

      <div className="tasks-section">
        <h2 className="tasks-title">Дела в работе</h2>
        <div className="task-item">
          <div className="task-icon">
            <svg width="52" height="52" viewBox="0 0 52 52" fill="none">
              <rect width="52" height="52" rx="15" fill="#F4F5F7" />
              <path
                d="M16.5 35.7465H35.5"
                stroke="black"
                strokeWidth="2"
                strokeLinecap="round"
              />
              <rect
                x="12"
                y="16.2535"
                width="28"
                height="16"
                rx="4"
                fill="black"
              />
              <circle cx="26.0266" cy="24.2535" r="3" fill="#F4F5F7" />
              <path
                d="M34.1039 18.6877H35.1039C36.2085 18.6877 37.1039 19.5832 37.1039 20.6877V21.6877"
                stroke="#F4F5F7"
                strokeLinecap="round"
                strokeLinejoin="round"
              />
              <path
                d="M17.8961 29.386H16.8961C15.7915 29.386 14.8961 28.4906 14.8961 27.386V26.386"
                stroke="#F4F5F7"
                strokeLinecap="round"
                strokeLinejoin="round"
              />
            </svg>
          </div>
          <div className="task-details">
            <div className="task-name">Оплатить</div>
            <div className="task-description">Входящие счета и налоги</div>
          </div>
        </div>
      </div>
    </div>
  );
}

export default HomePage;
