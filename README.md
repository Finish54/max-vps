# MAX VPS

**Современный VPN-сервис** на базе VPNFlashBot (Telegram-бот) + Flutter Web сайт + FastAPI backend.

🌐 **Сайт:** https://maxvps.online (планируется)
🤖 **Бот:** https://t.me/MAX_VPS_BOT (планируется)

---

## 🏗 Архитектура

```
Finish54/max-vps/                 ← monorepo
├── bot/                          ← клон VPNFlashBot (референс)
├── backend/                      ← FastAPI (Python 3.11+) — основной API
├── frontend/                     ← Flutter Web 3.x — сайт + Telegram Mini App
├── seo/                          ← статика для индексации (Flutter SPA плохо SEO)
├── docs/                         ← архитектура, дизайн, security, deploy
└── scripts/                      ← wg-setup, pg-grants, smoke-test, backup
```

## 🎯 Что это

- 💰 **Продажа VPN-подписок** через сайт (в дополнение к Telegram-боту)
- 🔐 **JWT-авторизация** через 6-значный код из бота
- 💳 **13 платёжных систем** (Telegram Stars, ЮMoney, ЮKassa, CryptoBot, Cryptomus, Lava, WATA, Heleket, ...)
- 🎨 **Дизайн vlessi.me** (тёмная тема, Unbounded + Inter)
- 🇷🇺 Только русский
- 📱 **Бонус:** Flutter Web → потом iOS/Android/Telegram Mini App

## 🚀 Стек

| Слой | Технология |
|---|---|
| Frontend | Flutter 3.24+, Riverpod, go_router, dio, slang, Material 3 |
| Backend | FastAPI, SQLAlchemy 2.0 async, Alembic, Pydantic v2 |
| DB | PostgreSQL 16 (локально, **НЕ прод-БД бота**) |
| Proxy | nginx + Let's Encrypt |
| Security | fail2ban, ufw, JWT, rate-limit, CSP/HSTS |
| CI/CD | GitHub Actions |

## 📅 Разработка

Полный план: [`docs/PLAN.md`](docs/PLAN.md) (или `/root/MAX_VPS_PLAN_v3_FLUTTER.md` локально у Hermes)

**Фазы:**
- ✅ 0 — Подготовка (git repo, monorepo, установка софта)
- ⏳ 1 — Backend (FastAPI + JWT + 13 платежей + WS)
- ⏳ 2 — Flutter Web Frontend
- ⏳ 3 — Security Audit (обязательно)
- ⏳ 4 — Pre-Deploy Verification (обязательно)
- ⏳ 5 — Deploy (Hermes делает сам)
- ⏳ 6 — Post-Launch (мониторинг)
- 🎁 7 — Mobile + Telegram Mini App (бонус)

## 🛠 Разработка

```bash
# Backend
cd backend
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload

# Frontend
cd frontend
flutter pub get
flutter run -d chrome

# Migrations
cd backend
alembic upgrade head
```

## 📄 Лицензия

MIT — см. [LICENSE](LICENSE)

## 👥 Команда

- **Hermes** — оркестратор (Claude Sonnet / MiniMax-M3)
- **OpenCode TUI** — backend dev (Gemini 3.5 Flash)
- **OpenCode Telegram** — доп. задачи (OpenRouter)
- **GitHub MCP** — push/PR/issues
- **OpenClaw** — удалён ❌
