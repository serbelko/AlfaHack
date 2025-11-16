# Backend AlfaHack

Простой backend на FastAPI + PostgreSQL с авторизацией по JWT.

---

## 1. Работающие на данный момент эндпоинты

### Healthcheck

**GET** `/health`

- **200** – сервис жив  
  Ответ (пример):

```json
{"status": "ok"}
```

---

### Auth

#### 1. `POST /api/auth/login`

**Body:**

```json
{
  "login": "login",
  "password": "password"
}
```

**Успех:**

- **201 Created**

```json
{
  "token": "jwt_token_here"
}
```

**Ошибки:**

- **404 NOT FOUND** – если пользователя с таким `login` нет  
  ```json
  "NOT FOUND"
  ```

- **401 Unauthorized** – если пароль не подходит  
  ```json
  "wrong login or password"
  ```

---

#### 2. `GET /api/auth/`

Получение информации о текущем пользователе по JWT.

**Headers:**

```http
Authorization: Bearer <token>
```

**Успех:**

- **200 OK**

```json
{
  "username": "username",
  "login": "login"
}
```

**Ошибки:**

- **403 Forbidden** – при любой проблеме с токеном (нет заголовка, неправильный формат, невалидный/просроченный токен, пользователя не существует)

```json
"JWT not found"
```

---

#### 3. `GET /api/auth/logout`

Формальный logout: сервер ничего не хранит, ответственность за "забыть" токен лежит на клиенте.

**Headers:**

```http
Authorization: Bearer <token>
```

**Успех:**

- **200 OK**

```json
{}
```

**Ошибки:**

- **403 Forbidden**

```json
"JWT not found"
```

---

## 2. Эндпоинты для работы со счетами (Amount API)

**Важно:** Все эндпоинты для работы со счетами требуют JWT авторизации в заголовке `Authorization: Bearer <token>`. Данные счетов хранятся в отдельной БД `mock_db`, которая используется только для разработки.

### Переменные окружения для mock БД

Добавьте в `.env`:
```env
MOCK_POSTGRES_USER=mock_user
MOCK_POSTGRES_PASSWORD=mock_password
MOCK_POSTGRES_DB=mock_db
```

---

#### 1. `POST /api/amount/`

Создать новый счёт.

**Headers:**
```http
Authorization: Bearer <token>
Content-Type: application/json
```

**Body:**
```json
{
  "name": "Название счёта",
  "count": 1000.0
}
```

**Параметры:**
- `name` (string, обязательный) - имя счёта (уникальное)
- `count` (float, опциональный) - начальный баланс (по умолчанию 0.0)

**Успех:**
- **201 Created**
```json
{
  "count": 1000.0,
  "name": "Название счёта"
}
```

**Ошибки:**
- **403 Forbidden** - если нет JWT токена
```json
"JWT NOT FOUND"
```

- **401 Unauthorized** - если счёт с таким именем уже существует или баланс отрицательный
```json
"Некорректные данные"
```

---

#### 2. `GET /api/amount?name=string`

Получить данные по конкретному счёту.

**Headers:**
```http
Authorization: Bearer <token>
```

**Query параметры:**
- `name` (string, обязательный) - имя счёта

**Успех:**
- **200 OK**
```json
{
  "count": 123.45,
  "name": "string"
}
```

**Ошибки:**
- **403 Forbidden**
```json
"JWT NOT FOUND"
```

- **404 Not Found** - если счёт не найден
```json
"СЧЁТ НЕ НАЙДЕН"
```

---

#### 3. `GET /api/amount/`

Получить список всех счетов.

**Headers:**
```http
Authorization: Bearer <token>
```

**Успех:**
- **200 OK**
```json
{
  "amounts": [
    {"count": 123.45, "name": "Счёт 1"},
    {"count": 500.0, "name": "Счёт 2"}
  ],
  "limit_data": 2
}
```

**Ошибки:**
- **403 Forbidden**
```json
"JWT NOT FOUND"
```

---

#### 4. `GET /api/amount/transaction?name=string`

Получить данные о последней транзакции по счёту.

**Headers:**
```http
Authorization: Bearer <token>
```

**Query параметры:**
- `name` (string, обязательный) - имя счёта

**Успех:**
- **200 OK**
```json
{
  "type": "income",
  "category": "зарплата",
  "count": 50000.0
}
```

Если транзакций нет, возвращается пустой объект: `{}`

**Ошибки:**
- **403 Forbidden**
```json
"JWT NOT FOUND"
```

- **404 Not Found** - если счёт не найден
```json
"СЧЁТ НЕ НАЙДЕН"
```

---

#### 5. `GET /api/amount/history?name=string&from=date&to=date&type=string`

Получить историю транзакций по счёту с возможностью фильтрации.

**Headers:**
```http
Authorization: Bearer <token>
```

**Query параметры:**
- `name` (string, обязательный) - имя счёта
- `from` (string, опциональный) - начало периода в формате YYYY-MM-DD
- `to` (string, опциональный) - конец периода в формате YYYY-MM-DD
- `type` (string, опциональный) - тип транзакции: `input` (доход) или `output` (расход)

**Успех:**
- **200 OK**
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

**Ошибки:**
- **403 Forbidden**
```json
"JWT NOT FOUND"
```

- **401 Unauthorized** - некорректный формат даты или типа транзакции
```json
"Incorrect type of request"
```

- **404 Not Found** - если счёт не найден
```json
"СЧЁТ НЕ НАЙДЕН"
```

**Примеры запросов:**
- Получить все транзакции: `GET /api/amount/history?name=Мой%20счёт`
- За период: `GET /api/amount/history?name=Мой%20счёт&from=2024-01-01&to=2024-01-31`
- Только доходы: `GET /api/amount/history?name=Мой%20счёт&type=input`
- Только расходы: `GET /api/amount/history?name=Мой%20счёт&type=output`

---

#### 6. `POST /api/amount/transaction`

Добавить новую транзакцию к счёту.

**Headers:**
```http
Authorization: Bearer <token>
Content-Type: application/json
```

**Body:**
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

**Успех:**
- **200 OK**
```json
{}
```

**Ошибки:**
- **403 Forbidden**
```json
"JWT NOT FOUND"
```

- **404 Not Found** - если счёт не найден
```json
"СЧЁТ НЕ НАЙДЕН"
```

- **401 Unauthorized** - некорректный тип транзакции, отрицательная или нулевая сумма
```json
"Некорректные данные"
```

**Примеры использования:**

Добавить доход:
```json
{
  "name": "Мой счёт",
  "type": "income",
  "category": "зарплата",
  "count": 50000.0
}
```

Добавить расход:
```json
{
  "name": "Мой счёт",
  "type": "outcome",
  "category": "еда",
  "count": 1500.0
}
```

---

### Типы транзакций

- **income** - доход (пополнение счёта)
- **outcome** - расход (списание со счёта)

В API истории транзакций также поддерживаются синонимы:
- `input` = `income` (доход)
- `output` = `outcome` (расход)

---

## 3. Инструкция по запуску приложения

### Предварительные условия

- Установлен Docker и Docker Compose.
- В корне проекта есть файл `.env` с настройками, например:

```env
POSTGRES_HOST=db
POSTGRES_PORT=5432
POSTGRES_USER=app_user
POSTGRES_PASSWORD=app_password
POSTGRES_DB=app_db

DATABASE_URL=postgresql://app_user:app_password@db:5432/app_db
ASYNC_DATABASE_URL=postgresql+asyncpg://app_user:app_password@db:5432/app_db

# Mock БД (для mock-service со счетами)
MOCK_POSTGRES_USER=mock_user
MOCK_POSTGRES_PASSWORD=mock_password
MOCK_POSTGRES_DB=mock_db

ACCESS_TOKEN_EXPIRE_MINUTES=60
SECRET_KEY=change_me_to_long_random_secret_key
PASSWORD_MIN_LENGTH=8
ALGORITHM=HS256
```

### Запуск через Docker

В корне репозитория (где лежит `docker-compose.yaml`):

```bash
docker compose up --build
```

Что делает команда:

- поднимает контейнер `db` (PostgreSQL для основной БД),
- поднимает контейнер `mock_db` (PostgreSQL для mock БД со счетами),
- собирает и запускает контейнер `app` (FastAPI backend).

После успешного старта:

- API доступно по адресу: `http://localhost:8000`
- healthcheck: `GET http://localhost:8000/health`
- auth: `POST http://localhost:8000/api/auth/login` и т.д.

Для перезапуска:
```bash
docker compose up -d --build
```

Для просмотра логов:
```bash
docker compose logs -f
```

Для остановки:

```bash
docker compose down
```

---

## 4. Инструкция по тестированию

### 3.1. Скрипт создания тестовых пользователей

В проекте есть скрипт сидера `app/scripts/seed_users.py`, который добавляет в БД тестовых пользователей (например, `admin` и `test`), если их ещё нет.

**Запуск через Docker (рекомендуется):**

```bash
docker compose run --rm app python -m app.scripts.seed_users
```

или если контейнер `app` уже запущен:

```bash
docker compose exec app python -m app.scripts.seed_users
```
```bash
docker compose exec app python -m app.scripts.seed_amounts
```

Скрипт:

- использует `UsersService` и `UsersRepository`,
- не дублирует пользователей: при повторном запуске пишет, что логин уже существует и пропускает.

После этого можно залогиниться. Пример тестовых данных

```json
{
                "username": "Admin",
                "login": "admin",
                "password": "admin12345",
            }
            {
                "username": "Test User",
                "login": "test",
                "password": "test12345",
            }
```

---

### 3.2. Как посмотреть данные в БД PostgreSQL

#### Вариант 1: через `psql` внутри контейнера

1. Зайти в контейнер PostgreSQL:

```bash
docker compose exec -it db sh
# или:
# docker compose exec -it db bash
```

2. Подключиться к базе:

```bash
psql -U "$POSTGRES_USER" -d "$POSTGRES_DB"
# если переменные не подтянулись, то явно:
# psql -U app_user -d app_db
```

3. Базовые команды `psql`:

- список таблиц:

  ```sql
  \dt
  ```

- описание таблицы `users`:

  ```sql
  \d users
  ```

- посмотреть содержимое таблицы `users`:

  ```sql
  SELECT * FROM users;
  ```

  или ограниченно:

  ```sql
  SELECT id, username, login FROM users LIMIT 10;
  ```

4. Выход из `psql`:

```sql
\q
```

5. Выход из контейнера:

```bash
exit
```

#### Вариант 2: локальный `psql` с хоста

Если у тебя установлен `psql` на машине и в `docker-compose.yaml` проброшен порт `5432:5432`, можно подключиться прямо с хоста:

```bash
psql -h localhost -p 5432 -U app_user -d app_db
```

Дальше команды те же (`\dt`, `SELECT ...` и т.п.).
