# 📐 Архитектура VPNFlashBot — анализ кода

**Цель:** понять как устроен бот, чтобы воспроизвести логику в FastAPI backend (MAX VPS).
**Источник:** `/root/projects/max-vps/bot/` (клон VPNFlashBot)
**Дата анализа:** 20.06.2026

---

## 📊 Общая статистика

| Метрика | Значение |
|---|---|
| **Всего Python LOC** | 13 795 |
| **Файлов .py** | 75 |
| **Handlers (user + admin)** | 13 файлов, 5 694 LOC |
| **Database (модели + методы)** | 1 845 LOC |
| **Misc (платежи, VPN, утилиты)** | 4 083 LOC |
| **Миграции Alembic** | 6 файлов |
| **Платёжных интеграций** | 12 (CryptoBot, Cryptomus, FreeKassa, KassaSmart, Lava, Stars, Tinkoff, WATA, Wawa, YooMoney, Heleket) |

---

## 🏗 Технологический стек бота

| Слой | Технология | Версия (примерно) |
|---|---|---|
| Telegram Bot | **aiogram** | 3.x |
| FSM | aiogram FSM (MemoryStorage) | встроенный |
| Database ORM | **SQLAlchemy** (async) | 2.x |
| DB driver | **asyncpg** (PostgreSQL) | — |
| Migrations | **Alembic** | — |
| Scheduler | **APScheduler** (AsyncIOScheduler) | — |
| Message broker | **NATS JetStream** | 2.10 |
| HTTP client | **httpx** (async) | — |
| Cache | **dogpile.cache** (memory) | — |
| Config | **python-dotenv** + кастомный Config | — |
| Container | Docker (compose) | — |
| Image | `python:3.x` | — |

---

## 📋 Структура кода

```
bot/                          # корень
├── main.py                   # 106 строк — точка входа
├── database/
│   ├── main.py               # engine + cache
│   ├── models/main.py        # 243 строки — SQLAlchemy модели
│   ├── methods/
│   │   ├── get.py            # 694 строк — все SELECT-запросы
│   │   ├── insert.py         # 202 строк — INSERT
│   │   ├── update.py         # 432 строк — UPDATE
│   │   └── delete.py         # 121 строк — DELETE
│   └── importBD/             # миграция со старой БД
├── handlers/
│   ├── user/                 # 5 694 строк — юзер-флоу
│   │   ├── main.py           # /start, главное меню (548 строк)
│   │   ├── keys_user.py      # ключи, продление (333 строк)
│   │   ├── payment_user.py   # оплата (451 строк)
│   │   ├── referral_user.py  # реферальная программа (426 строк)
│   │   └── free_vpn.py       # бесплатный VPN (96 строк)
│   ├── admin/                # 9 файлов — админка
│   │   ├── main.py           # /admin вход
│   │   ├── user_management.py # управление юзерами (725)
│   │   ├── location_control.py # локации/серверы (772)
│   │   ├── protocol_control.py # протоколы VLESS (662)
│   │   ├── static_user_control.py # статические ключи (332)
│   │   ├── keys_control.py   # управление ключами (227)
│   │   ├── group_mangment.py # группы (316)
│   │   ├── referal_admin.py  # рефералы админ (305)
│   │   └── metric_management.py # метрики (217)
│   └── other/main.py         # другие роуты
├── misc/
│   ├── util.py               # 252 строк — Config class
│   ├── loop.py               # 183 строк — главный loop (удаление ключей каждые 15с)
│   ├── callbackData.py       # 268 строк — FSM callback data
│   ├── language.py           # 85 строк — локализация
│   ├── commands.py           # 13 строк — команды бота
│   ├── nats_connect.py       # 11 строк — NATS init
│   ├── start_consumers.py    # 32 строк — NATS consumer
│   ├── VPN/
│   │   ├── ServerManager.py  # 76 строк — высокоуровневый менеджер
│   │   ├── BaseVpn.py        # 32 строк — базовый класс
│   │   └── Xui/
│   │       ├── XuiBase.py    # 103 строк — базовый x-ui
│   │       ├── Vless.py      # 101 строк — VLESS-специфика
│   │       └── XuiApiClient.py # 325 строк — async HTTP клиент
│   ├── Payment/              # 12 платёжных интеграций
│   │   ├── payment_systems.py # 331 строк — роутер платежей
│   │   ├── Stars.py          # Telegram Stars (144)
│   │   ├── YooMoney.py       # (95)
│   │   ├── Cryptomus.py      # (168)
│   │   ├── CryptoBot.py      # (82)
│   │   ├── Lava.py           # (90)
│   │   ├── KassaSmart.py     # (158)
│   │   ├── Tinkoff.py        # (82)
│   │   ├── FreeKassaBeta.py  # (68)
│   │   ├── Wawa.py           # (155)
│   │   ├── heleket.py        # (Heleket)
│   │   └── wata/             # модульный WATA (webhook, payment, client...)
│   └── remove_key_servise/   # NATS pub/sub для удаления ключей
├── filters/
│   ├── is_private.py         # только личка
│   ├── check_follow.py       # проверка подписки на канал
│   └── check_free_vpn.py     # фильтр бесплатного VPN
├── middlewares/
│   └── session.py            # DbSession middleware
├── keyboards/                # inline + reply клавиатуры
├── service/
│   ├── server_controll_manager.py # 131 строк — проверка серверов каждые 15 мин
│   ├── edit_message.py       # редактирование сообщений
│   ├── excel_service.py      # экспорт в Excel
│   ├── create_file_str.py    # генерация vless:// ссылок
│   ├── send_dump.py          # ежедневный дамп БД
│   └── service.py            # service-уровень
├── filters/
├── alembic/versions/         # 6 миграций
└── locale/{ru,en}/
```

---

## 🗄 База данных (PostgreSQL)

### Все таблицы (13 штук)

| Таблица | Модель | Назначение |
|---|---|---|
| `users` | `Persons` | Пользователи (tgid, banned, trial, referral, balance, lang, metric, group) |
| `keys` | `Keys` | VPN-ключи (user_tgid, subscription, server, switch_location, free_key, trial) |
| `donate` | `Donate` | Донаты (username, price) |
| `servers` | `Servers` | Серверы (type_vpn, panel, login/password/**api_token**/**sub_path**, ip, inbound_id) |
| `vds` | `Vds` | VDS-ноды (name, ip, password, location) |
| `location` | `Location` | Локации (name, pay_switch, group) |
| `groups` | `Groups` | Группы локаций (name) |
| `payments` | `Payments` | Платежи (user, id_payment, month_count, payment_system, amount, data) |
| `static_persons` | `StaticPersons` | Статические ключи (name, server) |
| `promocode` | `PromoCode` | Промокоды (text, percent, count_use) |
| `person_promocode_association` | `Table` | M2M юзер↔промокод (с полем `use`) |
| `withdrawal_requests` | `WithdrawalRequests` | Запросы на вывод средств (amount, payment_info, check_payment) |
| `metric` | `Metric` | UTM-метки (text, code) |
| `not_remove_key` | `NotRemoveKey` | Защищённые от удаления ключи |

### Связи (relationships)

```
Groups 1:N Locations 1:N Vds 1:N Servers 1:N Keys
                                    ↑
                                    └─── N:1 Persons (users)
Persons 1:N Keys
Persons 1:N Payments
Persons 1:N WithdrawalRequests
Persons M:N PromoCode (через person_promocode_association)
Persons N:1 Groups
Persons N:1 Metric
StaticPersons N:1 Servers
```

### 🔑 Ключевые особенности моделей

1. **`servers.api_token` и `sub_path`** — добавлены в новых миграциях `c3f8a1d20e91` и `d7a4b2c1e9f3` (нет в старом VPNHubBot) — для Bearer-авторизации в 3x-ui v2+
2. **`users.tgid`** — BigInteger, уникальный. Это основной идентификатор пользователя (из Telegram)
3. **`keys.user_tgid`** — BigInteger, FK на `users.tgid` (не на id!). Это критично
4. **`payments.id_payment`** — строковый ID платежа от внешней системы
5. **`metric.code`** — уникальный код для трекинга реферальных ссылок (`/start metric_code`)

---

## 🔄 Главные процессы

### 1. Bot startup (`main.py:start_bot`)

```
1. Connect to NATS (servers = "nats://nats:4222")
2. Create Dispatcher + register 4 routers:
   - registered_router  (для новых пользователей)
   - user_router        (для всех)
   - admin_router       (для админа)
   - other_router
3. Filter messages: only private chats
4. (Optional) Import old DB if IMPORT_DB=1
5. Create async SQLAlchemy sessionmaker
6. Add DbSessionMiddleware to dispatcher
7. Start APScheduler:
   - loop()         — каждые 15 секунд (удаление истёкших ключей)
   - send_dump()    — ежедневно в 00:00 (дамп БД в Telegram)
   - server_control_manager() — каждые 15 минут (проверка серверов)
8. Start polling + JetStream consumer (delete keys)
```

### 2. Главный loop (`misc/loop.py`) — каждые 15 секунд

```python
# Упрощённый алгоритм:
1. Получить все истёкшие ключи из БД (subscription < current_timestamp)
2. Для каждого:
   a. Если ключ в not_remove_key → пропустить
   b. Удалить клиента на сервере через XuiApiClient.delete_client()
   c. Удалить запись из БД
3. Получить серверы с превышением лимита (alert_server_space)
4. Уведомить админа в Telegram
```

### 3. JetStream consumer (`start_consumers.py`)

- Subject: `aiogram.remove.key`
- Stream: `DeleteKeyStream`
- При получении события удаления — асинхронно удалить ключ через XuiApiClient.

### 4. User flow (главные сценарии)

**`/start`** → проверка подписки на канал → метрика → создание юзера → главное меню

**Главное меню** (inline кнопки):
- 🔑 Подключиться к VPN
- 💳 Продлить подписку
- 🎁 Промокод
- 👥 Реферальная программа
- 🌍 Сменить язык
- ❓ Помощь

**Создание ключа:**
1. Выбор локации (Location)
2. Выбор протокола (TypeVpn, сейчас только VLESS)
3. Выбор месяцев (1, 3, 6, 12) → расчёт цены
4. Выбор платёжной системы → создание платежа → редирект/QR
5. После оплаты (webhook) → создание клиента в 3x-ui → запись в `keys`

### 5. XuiApiClient (`misc/VPN/Xui/XuiApiClient.py`) — 325 строк

**Возможности:**
- Поддержка **Bearer токена** (новый метод 3x-ui v2+)
- Поддержка **Cookie-сессии** через login/password (старый метод)
- **Авто-определение версии** панели (sanaei vs alireza)
- **Парсинг клиентов** из обоих форматов (settings JSON + clientStats)
- Методы:
  - `get_inbounds()`, `get_inbound(id)`
  - `get_client_by_email(email)`
  - `add_client(inbound_id, uuid, email, flow, limit_ip, total_gb, sub_id)`
  - `delete_client(inbound_id, uuid)`
  - `get_client_traffic(email)` → GB
  - `get_all_clients(inbound_id)`

### 6. Платёжная система (`misc/Payment/payment_systems.py`) — 331 строка

**Роутер платежей:**
- 12 платёжных классов (один на систему)
- Каждый наследует базовый интерфейс с методами:
  - `create_payment(amount, user_id, months, type)` → `(payment_id, redirect_url, qr)`
  - `check_payment(payment_id)` → `status`
  - `process_webhook(request_data)` → `is_valid`

**Webhook'и:**
- Каждая система настраивает свой URL (например `/webhook/yookassa`)
- При получении — проверка подписи → обновление платежа → выдача ключа

---

## 🔐 Конфигурация (Config class, `misc/util.py`)

Все секреты читаются из `.env`:

**Обязательные (raise если пусто):**
- `ADMIN_TG_ID`, `TG_TOKEN`, `NAME`, `LANGUAGES`, `POSTGRES_DB/USER/PASSWORD`
- `MONTH_COST` (через запятую), `TRIAL_PERIOD`, `FREE_SWITCH_LOCATION`, `UTC_TIME`
- `PRICE_SWITCH_LOCATION`, `LIMIT_IP`, `LIMIT_GB`, `REFERRAL_DAY/PERCENT`
- `MINIMUM_WITHDRAWAL_AMOUNT`, `FREE_SERVER`, `LIMIT_GB_FREE`, `SHOW_DONATE`

**Опциональные (платёжки, могут быть пустыми):**
- `YOOMONEY_TOKEN/WALLET`, `YOOKASSA_SHOP_ID/SECRET_KEY`
- `CRYPTOMUS_KEY/UUID`, `CRYPTO_BOT_API`, `LAVA_TOKEN_SECRET/ID_PROJECT`
- `WATA_TOKEN_CARD/SBP/VISA`, `HELEKET_KEY/UUID`, `TG_STARS`, `TG_STARS_DEV`

**Дополнительные:**
- `CHECK_FOLLOW`, `ID_CHANNEL`, `LINK_CHANNEL`, `NAME_CHANNEL`
- `FONT_TEMPLATE`, `NATS_URL` (для debug)
- `IMPORT_DB` (миграция со старой БД)

---

## 🧬 Что нам нужно воспроизвести в MAX VPS backend

### 1. SQLAlchemy модели

Переписать те же 13 таблиц **на PostgreSQL** (локальный на Server D), плюс **2 новые**:
- `web_users` — связь tgid ↔ web_session
- `web_sessions` — JWT refresh токены

### 2. Endpoints (минимум для ЛК + оплаты)

| Endpoint | Что делает | Источник в боте |
|---|---|---|
| `GET /api/me` | Данные юзера | `Persons` |
| `GET /api/keys` | Список ключей | `Keys` + `Servers` |
| `GET /api/keys/{id}/config` | vless:// ссылка | `create_file_str.py` |
| `GET /api/servers` | Все серверы | `Servers` |
| `GET /api/locations` | Локации | `Location` + `Vds` |
| `GET /api/payments` | История платежей | `Payments` |
| `POST /api/auth/telegram-code` | Код → JWT | (новое) |
| `POST /api/auth/refresh` | Refresh токен | (новое) |
| `POST /api/payments/create` | Создать платёж | `payment_systems.py` |
| `POST /api/payments/webhook/{system}` | Webhook'и | `payment_systems.py` |
| `WS /ws/notifications` | Real-time события | (новое) |

### 3. XuiApiClient

**Скопировать 1-в-1** в `backend/app/services/xui_client.py`. Код 325 строк — отлично написан, можно использовать.

### 4. Платёжные интеграции

Начать с **3 базовых**:
- **Telegram Stars** (без webhook — обновления через polling)
- **ЮKassa** (самый популярный в РФ)
- **CryptoBot** (простой API)

Остальные 10 — переносить постепенно.

### 5. Главный loop (15 сек) + NATS consumer

Переписать как **APScheduler job в FastAPI**:
- Каждые 15 секунд — проверка истёкших ключей + удаление
- Без NATS — проще через прямой вызов в job (для начала)

### 6. Telegram-бот mini

Минимальный бот:
- Обработчик `🔑 Войти на сайт` → генерит 6-значный код → сохраняет в Redis (или PostgreSQL таблицу `web_codes`)
- WebSocket уведомления от FastAPI → бот → отправка в Telegram

---

## 🚀 Что мы НЕ трогаем

- ❌ **Существующий VPNFlashBot** на Server B (87.121.217.36) — продолжает работать
- ❌ **Прод-БД бота** — у нас **своя локальная PostgreSQL** на Server D
- ❌ **Webhook URL'ы платёжек** — пусть ведут на бот (он их и обрабатывает), наш backend только читает статусы

---

## 📝 Главные риски

| Риск | Решение |
|---|---|
| Расхождение схем БД | Делаем **полную миграцию** (`bot/alembic/versions/*.py` → `backend/alembic/versions/`) |
| Разные ключи платежей | Используем **те же `.env`** переменные, что и бот |
| Несовпадение API 3x-ui | `XuiApiClient` уже поддерживает обе версии (sanaei/alireza) |
| Потеря юзеров при миграции | На проде пока НЕ переключаем — оба работают параллельно |

---

## 🎯 Что мы УЖЕ умеем (взято из бота)

✅ Рабочий XuiApiClient (Bearer + Cookie, авто-определение версии)
✅ 13 платёжных систем (можно перенести код 1-в-1)
✅ SQLAlchemy async модели
✅ Главный loop удаления ключей
✅ Генерация vless:// ссылок

**Мы НЕ изобретаем велосипед — переиспользуем 80% кода бота в backend.**

---

**Следующий шаг:** Фаза 0.4 — анализ vlessi.me для дизайна лендинга.
