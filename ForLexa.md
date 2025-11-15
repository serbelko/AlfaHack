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

## 2. Инструкция по запуску приложения

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

- поднимает контейнер `db` (PostgreSQL),
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

## 3. Инструкция по тестированию

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
