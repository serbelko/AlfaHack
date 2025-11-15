# AlfaHack

## Стек

**Backend:**
- FastAPI
- PostgreSQL (основная БД + отдельная mock_db)
- SQLAlchemy (async)
- JWT авторизация

**Frontend:**
- React
- Vite

## Запуск

### Backend

1. Создайте файл `.env` в корне проекта со следующим содержимым:
```env
# Основная БД
POSTGRES_HOST=db
POSTGRES_PORT=5432
POSTGRES_USER=your_user
POSTGRES_PASSWORD=your_password
POSTGRES_DB=your_db
DATABASE_URL=postgresql://your_user:your_password@db:5432/your_db
ASYNC_DATABASE_URL=postgresql+asyncpg://your_user:your_password@db:5432/your_db

# Mock БД (для mock-service)
MOCK_POSTGRES_USER=mock_user
MOCK_POSTGRES_PASSWORD=mock_password
MOCK_POSTGRES_DB=mock_db

# JWT настройки
SECRET_KEY=your_secret_key_here
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
PASSWORD_MIN_LENGTH=8
```

2. Запустите через docker-compose:
```bash
docker-compose up
```

Backend будет доступен на `http://localhost:8000`

### Frontend

```bash
cd front
npm install
npm run dev
```

Frontend будет доступен на `http://localhost:4200`

## API Документация

После запуска backend, документация доступна по адресу:
- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`

## Эндпоинты

### Авторизация

#### POST /api/auth/login
Авторизация пользователя.

**Request Body:**
```json
{
    "login": "user_login",
    "password": "user_password"
}
```

**Response 201:**
```json
{
    "token": "jwt_token_here"
}
```

**Response 404:** "NOT FOUND"  
**Response 401:** "wrong login or password"

#### GET /api/auth/
Получить информацию о текущем пользователе.

**Headers:**
```
Authorization: Bearer <token>
```

**Response 200:**
```json
{
    "username": "username",
    "login": "login"
}
```

**Response 403:** "JWT not found"

#### GET /api/auth/logout
Выход из системы (удаление токена на клиенте).

**Headers:**
```
Authorization: Bearer <token>
```

**Response 200:** `{}`

---

### Счета (Amount API)

Все эндпоинты для работы со счетами требуют JWT авторизации.

**Важно:** Данные счетов хранятся в отдельной БД `mock_db`, которая используется только для разработки и должна быть удалена перед выходом на прод.

#### POST /api/amount/
Создать новый счёт.

**Headers:**
```
Authorization: Bearer <token>
Content-Type: application/json
```

**Request Body:**
```json
{
    "name": "Название счёта",
    "count": 1000.0
}
```

**Параметры:**
- `name` (string, обязательный) - имя счёта (уникальное)
- `count` (float, опциональный) - начальный баланс (по умолчанию 0.0)

**Response 201:**
```json
{
    "count": 1000.0,
    "name": "Название счёта"
}
```

**Response 403:** "JWT NOT FOUND"  
**Response 401:** "Некорректные данные" (если счёт с таким именем уже существует или баланс отрицательный)

**Пример использования:**
```bash
curl -X POST "http://localhost:8000/api/amount/" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"name": "Мой счёт", "count": 5000.0}'
```

#### GET /api/amount?name=string
Получить данные по конкретному счёту.

**Headers:**
```
Authorization: Bearer <token>
```

**Query параметры:**
- `name` (string, обязательный) - имя счёта

**Response 200:**
```json
{
    "count": 123.45,
    "name": "string"
}
```

**Response 403:** "JWT NOT FOUND"  
**Response 404:** "СЧЁТ НЕ НАЙДЕН"

**Пример использования:**
```bash
curl -X GET "http://localhost:8000/api/amount?name=Мой%20счёт" \
  -H "Authorization: Bearer YOUR_TOKEN"
```

#### GET /api/amount/
Получить список всех счетов.

**Headers:**
```
Authorization: Bearer <token>
```

**Response 200:**
```json
{
    "amounts": [
        {"count": 123.45, "name": "Счёт 1"},
        {"count": 500.0, "name": "Счёт 2"}
    ],
    "limit_data": 2
}
```

**Response 403:** "JWT NOT FOUND"

**Пример использования:**
```bash
curl -X GET "http://localhost:8000/api/amount/" \
  -H "Authorization: Bearer YOUR_TOKEN"
```

#### GET /api/amount/transaction?name=string
Получить данные о последней транзакции по счёту.

**Headers:**
```
Authorization: Bearer <token>
```

**Query параметры:**
- `name` (string, обязательный) - имя счёта

**Response 200:**
```json
{
    "type": "income",
    "category": "зарплата",
    "count": 50000.0
}
```

Если транзакций нет, возвращается пустой объект: `{}`

**Response 403:** "JWT NOT FOUND"  
**Response 404:** "СЧЁТ НЕ НАЙДЕН"

**Пример использования:**
```bash
curl -X GET "http://localhost:8000/api/amount/transaction?name=Мой%20счёт" \
  -H "Authorization: Bearer YOUR_TOKEN"
```

#### GET /api/amount/history?name=string&from=date&to=date&type=string
Получить историю транзакций по счёту с возможностью фильтрации.

**Headers:**
```
Authorization: Bearer <token>
```

**Query параметры:**
- `name` (string, обязательный) - имя счёта
- `from` (string, опциональный) - начало периода в формате YYYY-MM-DD
- `to` (string, опциональный) - конец периода в формате YYYY-MM-DD
- `type` (string, опциональный) - тип транзакции: `input` (доход) или `output` (расход)

**Response 200:**
```json
{
    "name": "Мой счёт",
    "transaction": [
        {
            "type": "income",
            "category": "зарплата",
            "count": 50000.0
        },
        {
            "type": "outcome",
            "category": "еда",
            "count": 1500.0
        }
    ],
    "limit_data": 2
}
```

**Response 403:** "JWT NOT FOUND"  
**Response 401:** "Incorrect type of request" (некорректный формат даты или типа транзакции)  
**Response 404:** "СЧЁТ НЕ НАЙДЕН"

**Примеры использования:**
```bash
# Получить все транзакции
curl -X GET "http://localhost:8000/api/amount/history?name=Мой%20счёт" \
  -H "Authorization: Bearer YOUR_TOKEN"

# Получить транзакции за период
curl -X GET "http://localhost:8000/api/amount/history?name=Мой%20счёт&from=2024-01-01&to=2024-01-31" \
  -H "Authorization: Bearer YOUR_TOKEN"

# Получить только доходы
curl -X GET "http://localhost:8000/api/amount/history?name=Мой%20счёт&type=input" \
  -H "Authorization: Bearer YOUR_TOKEN"

# Получить только расходы
curl -X GET "http://localhost:8000/api/amount/history?name=Мой%20счёт&type=output" \
  -H "Authorization: Bearer YOUR_TOKEN"
```

#### POST /api/amount/transaction
Добавить новую транзакцию к счёту.

**Headers:**
```
Authorization: Bearer <token>
Content-Type: application/json
```

**Request Body:**
```json
{
    "name": "имя счёта",
    "type": "income",
    "category": "зарплата",
    "count": 50000.0
}
```

**Параметры:**
- `name` (string, обязательный) - имя счёта
- `type` (string, обязательный) - тип транзакции: `income` (доход) или `outcome` (расход)
- `category` (string, обязательный) - категория транзакции (например: "зарплата", "еда", "бытовые расходы", "зал")
- `count` (float, обязательный) - сумма транзакции (должна быть > 0)

**Примечание:** При создании транзакции баланс счёта автоматически обновляется:
- Для `income` - баланс увеличивается на `count`
- Для `outcome` - баланс уменьшается на `count`

**Response 200:** `{}`

**Response 403:** "JWT NOT FOUND"  
**Response 404:** "СЧЁТ НЕ НАЙДЕН"  
**Response 401:** "Некорректные данные" (некорректный тип транзакции, отрицательная или нулевая сумма)

**Примеры использования:**
```bash
# Добавить доход
curl -X POST "http://localhost:8000/api/amount/transaction" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Мой счёт",
    "type": "income",
    "category": "зарплата",
    "count": 50000.0
  }'

# Добавить расход
curl -X POST "http://localhost:8000/api/amount/transaction" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Мой счёт",
    "type": "outcome",
    "category": "еда",
    "count": 1500.0
  }'
```

## Типы транзакций

- **income** - доход (пополнение счёта)
- **outcome** - расход (списание со счёта)

В API истории транзакций также поддерживаются синонимы:
- `input` = `income` (доход)
- `output` = `outcome` (расход)

## Структура проекта

```
AlfaHack/
├── back/                    # Backend приложение
│   ├── app/
│   │   ├── api/            # API роутеры
│   │   │   ├── auth.py     # Авторизация
│   │   │   ├── amount.py   # Счета и транзакции
│   │   │   └── ping.py      # Health check
│   │   ├── core/           # Ядро приложения
│   │   │   ├── config.py   # Конфигурация
│   │   │   ├── db.py        # Модели БД
│   │   │   └── session.py   # Подключения к БД
│   │   ├── repo/           # Репозитории
│   │   ├── schemas/        # Pydantic схемы
│   │   └── services/       # Бизнес-логика
│   ├── main.py             # Точка входа
│   └── requirements.txt    # Зависимости
├── front/                   # Frontend приложение
├── docker-compose.yaml      # Docker конфигурация
└── .env                     # Переменные окружения
```

## Важные замечания

1. **Mock БД:** Счета и транзакции хранятся в отдельной БД `mock_db`. Перед выходом на прод необходимо:
   - Удалить сервис `mock_db` из `docker-compose.yaml`
   - Удалить volume `mock_postgres_data`
   - Удалить код работы с mock БД из приложения

2. **JWT токены:** Все эндпоинты для работы со счетами требуют валидный JWT токен в заголовке `Authorization: Bearer <token>`

3. **Баланс счёта:** Баланс счёта автоматически обновляется при создании транзакций через POST `/api/amount/transaction`
