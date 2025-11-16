const API_BASE_URL =
  import.meta.env.VITE_API_BASE_URL || "http://localhost:8000";

// здесь меняешь имя счёта, если хочешь реальный, а не заглушку
const DEFAULT_ACCOUNT_NAME = "test";

function buildHistoryQuery(params) {
  const search = new URLSearchParams();
  search.set("name", params.accountName || DEFAULT_ACCOUNT_NAME);
  if (params.from) search.set("from_date", params.from);
  if (params.to) search.set("to_date", params.to);
  return search.toString() ? `?${search.toString()}` : "";
}

function normalizeType(type) {
  const t = String(type || "").toLowerCase();
  if (t === "income" || t === "input") return "income";
  if (t === "outcome" || t === "output") return "expense";
  return "other";
}

function parseDate(value) {
  if (!value) return null;
  const d = new Date(value);
  if (Number.isNaN(d.getTime())) return null;
  return d;
}

function formatDayLabel(date) {
  const d = String(date.getDate()).padStart(2, "0");
  const m = String(date.getMonth() + 1).padStart(2, "0");
  return `${d}.${m}`;
}

const MONTH_LABELS = [
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
];

function buildChartData(transactions, period) {
  const txs = Array.isArray(transactions) ? transactions : [];
  if (txs.length === 0) {
    return {
      income: 0,
      expenses: 0,
      incomeData: [],
      expensesData: [],
      labels: [],
    };
  }

  let totalIncome = 0;
  let totalExpenses = 0;
  const groups = new Map();

  txs.forEach((tx) => {
    const dt = parseDate(tx.created_at);
    if (!dt) return;

    const kind = normalizeType(tx.type);
    if (kind === "other") return;

    const amount = Number(tx.count) || 0;

    if (kind === "income") totalIncome += amount;
    if (kind === "expense") totalExpenses += amount;

    let key;
    let label;
    if (period === "year") {
      const m = dt.getMonth();
      key = m.toString();
      label = MONTH_LABELS[m];
    } else {
      key = dt.toISOString().slice(0, 10);
      label = formatDayLabel(dt);
    }

    if (!groups.has(key)) {
      groups.set(key, { label, income: 0, expenses: 0 });
    }
    const g = groups.get(key);
    if (kind === "income") g.income += amount;
    if (kind === "expense") g.expenses += amount;
  });

  const sortedKeys = Array.from(groups.keys()).sort((a, b) => {
    if (period === "year") {
      return Number(a) - Number(b);
    }
    if (a < b) return -1;
    if (a > b) return 1;
    return 0;
  });

  const incomeData = [];
  const expensesData = [];
  const labels = [];

  sortedKeys.forEach((key) => {
    const g = groups.get(key);
    labels.push(g.label);
    incomeData.push(g.income);
    expensesData.push(g.expenses);
  });

  return {
    income: totalIncome,
    expenses: totalExpenses,
    incomeData,
    expensesData,
    labels,
  };
}

export async function getAnalyticsFromHistory(params) {
  const rawToken =
    localStorage.getItem("authToken") || localStorage.getItem("token");

  if (!rawToken) {
    return {
      income: 0,
      expenses: 0,
      incomeData: [],
      expensesData: [],
      labels: [],
    };
  }

  const lower = rawToken.toLowerCase();
  const authHeader = lower.startsWith("bearer ")
    ? rawToken
    : `Bearer ${rawToken}`;

  const query = buildHistoryQuery(params);

  const res = await fetch(`${API_BASE_URL}/api/amount/history${query}`, {
    method: "GET",
    headers: {
      "Content-Type": "application/json",
      Authorization: authHeader,
    },
  });

  if (res.status === 404) {
    // счёт не найден → для фронта это просто "нет данных" → рисуем мок
    return {
      income: 0,
      expenses: 0,
      incomeData: [],
      expensesData: [],
      labels: [],
    };
  }

  if (!res.ok) {
    const error = new Error("Failed to load history");
    error.status = res.status;
    throw error;
  }

  const data = await res.json();
  const transactions = Array.isArray(data.transaction) ? data.transaction : [];
  return buildChartData(transactions, params.period || "month");
}
