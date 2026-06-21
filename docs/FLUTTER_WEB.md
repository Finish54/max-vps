# 🦋 Flutter Web — технологии, SEO и best practices

**Цель:** правильно настроить Flutter Web для MAX VPS с хорошим SEO.
**Дата:** 20.06.2026
**Версии:** Flutter 3.24+, Dart 3.5+

---

## 📊 Главная проблема Flutter Web

Flutter Web — это **SPA** (Single Page Application):
- HTML почти пустой (только `<div id="app">` и загрузчик)
- Всё рендерится через JavaScript/Dart в canvas (Skia/WebGL)
- **Googlebot может не дождаться** рендера → пустая страница в индексе
- **Яндекс** ещё хуже — может не рендерить Flutter вообще

### Что мы НЕ хотим

- ❌ Пользователь ищет "VPN купить" → Google показывает пустую страницу MAX VPS
- ❌ Open Graph не подхватывается → при шаринге в Telegram нет превью
- ❌ Lighthouse SEO score = 0

---

## 🎯 Наша стратегия: **3 уровня SEO**

### Уровень 1: **Статическое SEO-зеркало** (папка `seo/`)

Для **публичных страниц** (лендинг, тарифы, FAQ) делаем **обычные HTML-файлы**:
- `seo/index.html` — копия лендинга (чистый HTML, без Flutter)
- `seo/pricing.html` — тарифы
- `seo/faq.html` — FAQ
- `seo/sitemap.xml` — все страницы
- `seo/robots.txt`

**Как работает:**
- nginx раздаёт `seo/` напрямую по путям `/`, `/pricing`, `/faq`
- Flutter Web грузится на `/app/*` (динамические страницы)
- Google видит нормальный HTML → индексирует

### Уровень 2: **Динамические meta-теги** в Flutter

Через пакет **`meta_seo`** (или ручную инжекцию в `document.head`):
- При навигации между страницами в Flutter — обновляем `<title>`, `<meta>`, `<og:*>`
- На SSR-страницах (уровень 1) — meta уже в HTML

### Уровень 3: **Cloudflare Prerender** (опционально, для Яндекс)

- Cloudflare Worker детектит ботов по User-Agent
- Бот получает prerender HTML (через Prerender.io или наш Puppeteer)
- Пользователь получает обычный Flutter SPA
- Для MAX VPS **не критично** на старте (Cloudflare нужен, оплата)

---

## 📦 Ключевые Flutter пакеты

### Обязательные

| Пакет | Версия | Зачем |
|---|---|---|
| `flutter_riverpod` | ^2.5 | State management |
| `go_router` | ^14 | URL-роутинг, deep links |
| `dio` | ^5 | HTTP client (intercept JWT) |
| `web_socket_channel` | ^3 | WebSocket для real-time |
| `google_fonts` | ^6 | Unbounded + Inter |
| `meta_seo` | ^1 | Meta-теги из Flutter |
| `universal_html` | ^2 | DOM доступ (для meta_seo) |
| `flutter_form_builder` | ^9 | Формы |
| `reactive_forms` | ^7 | Валидация |
| `slang` | ^4 | Compile-time i18n (только ru) |
| `intl` | ^0.19 | Дата/валюта |
| `freezed` | ^2 | Immutable модели |
| `json_serializable` | ^6 | JSON codegen |
| `build_runner` | ^2 | Codegen |
| `flutter_lints` | ^4 | Linting |
| `very_good_analysis` | ^6 | Strict linting |

### Опциональные

| Пакет | Зачем |
|---|---|
| `flutter_telegram_web` | Mini App для Telegram |
| `flutter_secure_storage` | JWT в localStorage |
| `cached_network_image` | Кэш картинок |
| `flutter_svg` | SVG иконки (логотип) |
| `lottie` | Анимации |
| `pwa_launcher` | PWA support |
| `share_plus` | Кнопка "Поделиться" |
| `url_launcher` | Открыть Telegram-канал |

---

## 🎨 Базовая структура Flutter Web

```
frontend/                          # Flutter Web app
├── lib/
│   ├── main.dart                  # Entry point
│   ├── app.dart                   # MaterialApp + Router
│   ├── core/                      # Ядро
│   │   ├── theme/
│   │   │   ├── app_theme.dart    # Material 3 + палитра vlessi
│   │   │   ├── app_colors.dart   # HEX-цвета
│   │   │   └── app_typography.dart # GoogleFonts + Unbounded
│   │   ├── api/
│   │   │   ├── api_client.dart   # Dio + interceptors
│   │   │   ├── api_exception.dart
│   │   │   └── endpoints.dart    # URL'ы
│   │   ├── auth/
│   │   │   ├── auth_service.dart # JWT в localStorage
│   │   │   ├── jwt_storage.dart
│   │   │   └── auth_interceptor.dart
│   │   ├── router/
│   │   │   └── app_router.dart   # go_router
│   │   ├── seo/
│   │   │   ├── seo_helper.dart   # meta_seo wrapper
│   │   │   └── seo_config.dart   # per-page meta
│   │   ├── widgets/
│   │   │   ├── app_button.dart
│   │   │   ├── app_card.dart
│   │   │   ├── app_scaffold.dart
│   │   │   └── responsive.dart   # breakpoints
│   │   └── utils/
│   ├── features/
│   │   ├── landing/
│   │   │   ├── presentation/
│   │   │   │   ├── landing_page.dart
│   │   │   │   ├── widgets/
│   │   │   │   │   ├── hero_section.dart
│   │   │   │   │   ├── features_section.dart
│   │   │   │   │   ├── pricing_section.dart
│   │   │   │   │   ├── faq_section.dart
│   │   │   │   │   └── footer.dart
│   │   │   └── ...
│   │   ├── auth/
│   │   │   ├── data/
│   │   │   ├── domain/
│   │   │   └── presentation/
│   │   ├── account/
│   │   ├── payment/
│   │   └── legal/
│   ├── l10n/
│   │   └── ru.strings.yaml      # slang конфиг
│   └── gen/                      # Generated (freezed, json)
├── web/                          # Flutter Web build config
│   ├── index.html                # Главный HTML (SEO!)
│   ├── manifest.json             # PWA manifest
│   ├── favicon.png
│   └── icons/
├── assets/
│   ├── fonts/                    # Local fallback fonts
│   ├── images/
│   └── icons/
├── test/
├── pubspec.yaml
├── analysis_options.yaml
└── Dockerfile
```

---

## 🌐 SEO-конфигурация в Flutter

### 1. `web/index.html` — базовые meta-теги

```html
<!DOCTYPE html>
<html lang="ru">
<head>
  <base href="/">
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=5">

  <!-- Primary Meta Tags -->
  <title>MAX VPS — VPN-подписки для дома и телефона</title>
  <meta name="title" content="MAX VPS — VPN-подписки для дома и телефона">
  <meta name="description" content="MAX VPS — надёжный VPN-сервис. VLESS-протокол, до 5 устройств, поддержка 24/7. Вход через Telegram.">
  <meta name="keywords" content="vpn, vless, vpn подписка, vpn россия, max vps, maxvps, купить vpn">
  <meta name="author" content="MAX VPS">

  <!-- Open Graph / Facebook -->
  <meta property="og:type" content="website">
  <meta property="og:url" content="https://maxvps.online/">
  <meta property="og:title" content="MAX VPS — VPN-подписки">
  <meta property="og:description" content="VLESS-протокол, до 5 устройств, поддержка 24/7.">
  <meta property="og:image" content="https://maxvps.online/og-image.png">
  <meta property="og:locale" content="ru_RU">
  <meta property="og:site_name" content="MAX VPS">

  <!-- Twitter -->
  <meta property="twitter:card" content="summary_large_image">
  <meta property="twitter:url" content="https://maxvps.online/">
  <meta property="twitter:title" content="MAX VPS — VPN-подписки">
  <meta property="twitter:description" content="VLESS-протокол, до 5 устройств, поддержка 24/7.">
  <meta property="twitter:image" content="https://maxvps.online/og-image.png">

  <!-- Theme -->
  <meta name="theme-color" content="#05080f">
  <meta name="msapplication-TileColor" content="#05080f">

  <!-- Favicon -->
  <link rel="icon" type="image/png" href="/favicon.png">
  <link rel="apple-touch-icon" href="/icons/Icon-192.png">

  <!-- Manifest -->
  <link rel="manifest" href="manifest.json">

  <!-- Fonts (preconnect для скорости) -->
  <link rel="preconnect" href="https://fonts.googleapis.com">
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
  <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&family=Unbounded:wght@300;400;500;700;900&display=swap" rel="stylesheet">

  <!-- Structured Data (JSON-LD) -->
  <script type="application/ld+json">
  {
    "@context": "https://schema.org",
    "@type": "Organization",
    "name": "MAX VPS",
    "url": "https://maxvps.online",
    "logo": "https://maxvps.online/logo.png",
    "description": "VPN-сервис на базе VLESS-протокола"
  }
  </script>

  <style>
    /* Loader до запуска Flutter */
    body { margin: 0; background: #05080f; }
    .loader { display: flex; align-items: center; justify-content: center;
              height: 100vh; color: #fff; font-family: Inter, sans-serif; }
  </style>
</head>
<body>
  <div id="app">
    <div class="loader">MAX VPS загружается...</div>
  </div>
  <script src="flutter_bootstrap.js" async></script>
</body>
</html>
```

### 2. Динамические meta-теги в Flutter

```dart
// lib/core/seo/seo_helper.dart
import 'package:meta_seo/meta_seo.dart';
import 'package:flutter/foundation.dart';

class SeoHelper {
  static void setPage({
    required String title,
    required String description,
    String? image,
    String? url,
  }) {
    if (!kIsWeb) return;
    final meta = MetaSEO();
    meta.title(title: title);
    meta.description(description: description);
    meta.keywords(keywords: 'vpn, vless, maxvps');
    if (image != null) meta.ogImage(image: image);
    if (url != null) meta.ogUrl(ogUrl: url);
  }
}

// Использование в landing_page.dart
@override
void initState() {
  super.initState();
  SeoHelper.setPage(
    title: 'MAX VPS — VPN-подписки',
    description: 'Надёжный VPN-сервис. VLESS, 5 устройств.',
  );
}
```

### 3. Роутинг с SEO-aware путями

```dart
// lib/core/router/app_router.dart
final router = GoRouter(
  initialLocation: '/',
  routes: [
    GoRoute(
      path: '/',
      builder: (context, state) => const LandingPage(),
    ),
    GoRoute(
      path: '/pricing',
      builder: (context, state) => const PricingPage(),
    ),
    GoRoute(
      path: '/faq',
      builder: (context, state) => const FaqPage(),
    ),
    GoRoute(
      path: '/login',
      builder: (context, state) => const LoginPage(),
    ),
    GoRoute(
      path: '/app/account',
      builder: (context, state) => const AccountPage(),
    ),
    GoRoute(
      path: '/app/account/keys',
      builder: (context, state) => const KeysPage(),
    ),
    GoRoute(
      path: '/terms',
      builder: (context, state) => const TermsPage(),
    ),
    // ... и т.д.
  ],
);
```

---

## 📄 Статическое SEO-зеркало (папка `seo/`)

Для Googlebot и Яндекса делаем **обычные HTML-файлы**, которые nginx раздаёт напрямую:

### `seo/index.html` (≈ копия лендинга)

```html
<!DOCTYPE html>
<html lang="ru">
<head>
  <meta charset="UTF-8">
  <title>MAX VPS — VPN-подписки для дома и телефона</title>
  <meta name="description" content="...">
  <!-- ... все meta-теги -->
  <link rel="canonical" href="https://maxvps.online/">
  <style>
    /* Полный CSS как в Flutter */
    body { font-family: Inter, sans-serif; background: #05080f; color: #fff; }
    /* ... */
  </style>
</head>
<body>
  <header>
    <h1>MAX VPS — VPN-подписки для дома и телефона</h1>
    <p>Надёжный VPN-сервис на базе VLESS-протокола...</p>
    <a href="/app/" class="cta">Войти через Telegram</a>
  </header>
  <section id="features">
    <!-- Преимущества как HTML -->
  </section>
  <section id="pricing">
    <!-- Тарифы как HTML -->
  </section>
  <section id="faq">
    <!-- FAQ как HTML -->
  </section>
  <footer>
    <a href="/terms">Соглашение</a>
    <a href="/privacy">Политика</a>
    <a href="/offer">Оферта</a>
  </footer>
</body>
</html>
```

### `seo/sitemap.xml`

```xml
<?xml version="1.0" encoding="UTF-8"?>
<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">
  <url>
    <loc>https://maxvps.online/</loc>
    <lastmod>2026-06-20</lastmod>
    <changefreq>weekly</changefreq>
    <priority>1.0</priority>
  </url>
  <url>
    <loc>https://maxvps.online/pricing</loc>
    <lastmod>2026-06-20</lastmod>
    <changefreq>weekly</changefreq>
    <priority>0.9</priority>
  </url>
  <url>
    <loc>https://maxvps.online/faq</loc>
    <lastmod>2026-06-20</lastmod>
    <changefreq>monthly</changefreq>
    <priority>0.7</priority>
  </url>
  <url>
    <loc>https://maxvps.online/terms</loc>
    <priority>0.3</priority>
  </url>
  <url>
    <loc>https://maxvps.online/privacy</loc>
    <priority>0.3</priority>
  </url>
  <url>
    <loc>https://maxvps.online/offer</loc>
    <priority>0.3</priority>
  </url>
  <url>
    <loc>https://maxvps.online/refund</loc>
    <priority>0.3</priority>
  </url>
</urlset>
```

### `seo/robots.txt`

```
User-agent: *
Allow: /
Disallow: /app/

Sitemap: https://maxvps.online/sitemap.xml
```

---

## ⚙️ nginx — раздача статики + Flutter

```nginx
server {
    listen 443 ssl http2;
    server_name maxvps.online;

    # SSL (Let's Encrypt)
    ssl_certificate /etc/letsencrypt/live/maxvps.online/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/maxvps.online/privkey.pem;

    # SEO-статика (читается напрямую nginx)
    location / {
        root /var/www/seo;
        try_files $uri $uri/ /index.html;
    }

    location = /sitemap.xml { root /var/www/seo; }
    location = /robots.txt { root /var/www/seo; }

    # Flutter Web SPA (всё остальное динамическое)
    location /app/ {
        root /var/www/flutter;
        try_files $uri $uri/ /app/index.html;
    }

    # Backend API
    location /api/ {
        proxy_pass http://127.0.0.1:8000/api/;
        proxy_http_version 1.1;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    # WebSocket
    location /ws/ {
        proxy_pass http://127.0.0.1:8000/ws/;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
    }

    # Security headers
    add_header X-Frame-Options "SAMEORIGIN" always;
    add_header X-Content-Type-Options "nosniff" always;
    add_header Referrer-Policy "strict-origin-when-cross-origin" always;
    add_header Content-Security-Policy "default-src 'self'; script-src 'self' 'unsafe-inline' https://fonts.googleapis.com; style-src 'self' 'unsafe-inline' https://fonts.googleapis.com; font-src https://fonts.gstatic.com; img-src 'self' data: https:;" always;
}
```

---

## 📱 Адаптив — Flutter breakpoints

```dart
// lib/core/widgets/responsive.dart
class Breakpoints {
  static const double mobile = 600;
  static const double tablet = 1024;
  static const double desktop = 1280;
}

bool isMobile(BuildContext context) =>
    MediaQuery.of(context).size.width < Breakpoints.tablet;

bool isDesktop(BuildContext context) =>
    MediaQuery.of(context).size.width >= Breakpoints.desktop;
```

**Layout план:**
- **Mobile (<600px)**: hamburger menu, single column, vertical pricing cards
- **Tablet (600-1024px)**: 2-column features, 2-column pricing
- **Desktop (>1024px)**: full nav, 3-column features, 3-column pricing

---

## 🧪 Lighthouse цели

| Метрика | Цель |
|---|---|
| Performance | ≥75 |
| SEO | ≥90 |
| Accessibility | ≥85 |
| Best Practices | ≥85 |

**Как достигаем:**
- Performance: Flutter Web 3.24+ быстрее, lazy load, оптимизированные ассеты
- SEO: meta-теги + статическое зеркало + sitemap
- A11y: Flutter имеет встроенную поддержку, тестируем через TalkBack
- BP: HTTPS, no console errors

---

## 🆚 Flutter Web vs Next.js — итоговое сравнение

| | Next.js | Flutter Web |
|---|---|---|
| **SEO из коробки** | ✅ отличный (SSR) | ⚠️ нужен костыли |
| **Bundle size** | ~150 КБ JS | ~2-5 МБ (Skia) |
| **Mobile позже** | переписывать | ✅ та же база |
| **Telegram Mini App** | ✅ ок | ✅ ок (flutter_telegram_web) |
| **Стоимость разработки** | ниже | выше |
| **Скорость разработки** | быстро | средне |
| **Production-ready для VPN-сервиса** | ✅ | ✅ с SEO-зеркалом |

**Для MAX VPS:**
- ✅ Flutter Web подходит (у нас есть Flutter-опыт, нужен Mobile потом)
- ✅ SEO закрываем 3-уровневой стратегией
- ✅ Bundle size компенсируем CDN + gzip

---

## 🎁 Бонус: Telegram Mini App

Flutter Web **отлично работает** как Mini App. После успешного Web-деплоя:
- Добавляем кнопку в боте «Открыть MAX VPS»
- Через `@BotFather` → Bot Settings → Menu Button → `/app/`
- В Flutter используем `flutter_telegram_web` для получения `initData`
- Авторизация через Telegram — **без логина/пароля**!

---

## 📋 TODO для Фазы 2 (Frontend)

- [ ] `flutter create max_vps_web --platforms=web`
- [ ] Настроить `pubspec.yaml` со всеми пакетами
- [ ] `analysis_options.yaml` с very_good_analysis
- [ ] `web/index.html` с meta-тегами
- [ ] `web/manifest.json` для PWA
- [ ] `lib/core/theme/` — палитра vlessi + шрифты
- [ ] `lib/core/router/` — go_router с SEO-aware путями
- [ ] `lib/core/seo/` — обёртка над meta_seo
- [ ] `seo/index.html`, `seo/pricing.html`, `seo/faq.html`
- [ ] `seo/sitemap.xml`, `seo/robots.txt`
- [ ] `lib/features/landing/` — 5 блоков лендинга
- [ ] `lib/features/auth/` — вход через Telegram
- [ ] `lib/features/account/` — ЛК (5 страниц)
- [ ] `lib/features/payment/` — 13 платежей (начнём с 3)
- [ ] `lib/features/legal/` — 4 юр. страницы
- [ ] Адаптив
- [ ] og:image 1200×630 (генерируем)
- [ ] favicon, apple-touch-icon
- [ ] Lighthouse ≥75 perf, ≥90 SEO
- [ ] Dockerfile для деплоя
- [ ] GitHub Actions: build + push Docker image
