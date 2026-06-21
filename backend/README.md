# MAX VPS Backend

FastAPI backend для сайта MAX VPS + Telegram Mini App.

## 🚀 Стек

- **FastAPI** 0.115+ — async web framework
- **SQLAlchemy** 2.0+ async + **asyncpg**
- **Pydantic** v2 + **pydantic-settings**
- **PostgreSQL** 16 (локальная на Server D)
- **Redis** 7 (rate-limit + кэш кодов)
- **aiogram** 3 (минимальный Telegram-бот для auth-кодов)
- **JWT** auth через код из бота
- **Alembic** миграции
- **Pytest** + httpx для тестов
- **Prometheus** метрики на `/metrics`

## 🏗 Структура

```
backend/
├── app/
│   ├── main.py              # FastAPI app + middleware
│   ├── core/
│   │   └── config.py        # Pydantic Settings
│   ├── db/
│   │   └── session.py       # SQLAlchemy async engine
│   ├── api/                 # TODO Фаза 1: endpoints
│   ├── security/            # TODO: JWT, rate-limit
│   ├── payments/            # TODO Фаза 1.7: 13 платежей
│   └── models/              # TODO Фаза 1.2: SQLAlchemy models
├── alembic/                 # TODO Фаза 1.3: миграции
├── tests/                   # pytest
├── scripts/                 # init_db.sql
├── Dockerfile
├── docker-compose.yml       # local dev: PG + Redis + backend
├── pyproject.toml
├── requirements.txt
└── .env.example
```

## 🛠 Локальная разработка

```bash
# 1. venv
python3 -m venv .venv
source .venv/bin/activate

# 2. install deps
pip install -r requirements-dev.txt

# 3. Generate JWT secret
python3 -c "import secrets; print('JWT_SECRET_KEY=' + secrets.token_urlsafe(64))" >> .env

# 4. copy env template
cp .env.example .env
# отредактируй .env — укажи свой JWT_SECRET_KEY

# 5. start services
docker compose up -d postgres redis

# 6. run migrations (Фаза 1.3 — пока no-op)
# alembic upgrade head

# 7. start backend
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

## 🧪 Тесты

```bash
pytest                       # все тесты
pytest -v                    # verbose
pytest --cov=app             # с покрытием
pytest tests/test_main.py    # один файл
```

## 🌐 Endpoints (после Фазы 1)

| Method | Path | Description |
|---|---|---|
| GET | `/` | Service info |
| GET | `/health` | Liveness probe |
| GET | `/health/ready` | Readiness probe (DB) |
| GET | `/docs` | Swagger UI |
| GET | `/redoc` | ReDoc |
| GET | `/openapi.json` | OpenAPI 3.1 schema |
| GET | `/metrics` | Prometheus metrics |
| POST | `/api/auth/telegram-code` | Обменять 6-значный код на JWT |
| POST | `/api/auth/refresh` | Refresh access token |
| GET | `/api/me` | Текущий пользователь |
| GET | `/api/keys` | Список VPN-ключей |
| GET | `/api/payments` | История платежей |
| GET | `/api/servers` | Серверы |
| GET | `/api/locations` | Локации |
| WS | `/ws/notifications` | Real-time уведомления |

## 🔐 Auth Flow

```
1. Юзер открывает сайт → Flutter Web SPA
2. Жмёт "Войти" → открывает Telegram-бота
3. В боте жмёт "🔑 Войти на сайт" → бот генерит 6-значный код
4. Код сохраняется в Redis (TTL 5 мин)
5. Юзер вводит код на сайте → POST /api/auth/telegram-code
6. Backend проверяет код в Redis → выдаёт JWT (15 мин) + refresh (7 дней)
7. Flutter сохраняет JWT в localStorage
8. Все запросы с заголовком Authorization: Bearer <jwt>
```

## 🚀 Деплой (Фаза 5)

```bash
docker build -t maxvps-backend:latest .
docker push ghcr.io/finish54/maxvps-backend:latest
ssh root@5.181.23.168 "docker pull ..."
```
