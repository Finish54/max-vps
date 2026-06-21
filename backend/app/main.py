"""
MAX VPS Backend - FastAPI application entry point.

Production-grade setup:
- CORS middleware (configurable origins)
- GZip compression
- Structured JSON logging
- Prometheus metrics endpoint
- Health check + startup/shutdown events
- Trusted hosts (anti Host header injection)
"""
from contextlib import asynccontextmanager
from typing import AsyncIterator

import structlog
from fastapi import FastAPI, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.gzip import GZipMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from fastapi.responses import JSONResponse, ORJSONResponse
from prometheus_client import Counter, Histogram
from sqlalchemy import text

from app import __version__
from app.core.config import settings

# === Structured logging ===
structlog.configure(
    processors=[
        structlog.contextvars.merge_contextvars,
        structlog.processors.add_log_level,
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.processors.JSONRenderer(),
    ],
    wrapper_class=structlog.make_filtering_bound_logger(
        getattr(__import__("logging"), settings.LOG_LEVEL)
    ),
    logger_factory=structlog.PrintLoggerFactory(),
    cache_logger_on_first_use=True,
)

log = structlog.get_logger()

# === Prometheus metrics ===
REQUEST_COUNT = Counter(
    "http_requests_total",
    "Total HTTP requests",
    ["method", "endpoint", "status"],
)
REQUEST_LATENCY = Histogram(
    "http_request_duration_seconds",
    "HTTP request latency",
    ["method", "endpoint"],
)


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncIterator[None]:
    """Startup + shutdown events."""
    log.info(
        "startup",
        app=settings.APP_NAME,
        version=__version__,
        env=settings.APP_ENV,
        debug=settings.DEBUG,
    )
    # TODO Фаза 1.2: init DB engine, Redis, NATS consumer
    yield
    log.info("shutdown", version=__version__)


# === App factory ===
def create_app() -> FastAPI:
    app = FastAPI(
        title=f"{settings.APP_NAME} API",
        description="MAX VPS — VPN-сервис. Backend для сайта + Telegram Mini App.",
        version=__version__,
        docs_url="/docs",
        redoc_url="/redoc",
        openapi_url="/openapi.json",
        default_response_class=ORJSONResponse,
        lifespan=lifespan,
    )

    # === Middleware (порядок важен: последний добавленный — первый выполняется) ===

    # 1. GZip (compressions всех ответов > 500 bytes)
    app.add_middleware(GZipMiddleware, minimum_size=500)

    # 2. Trusted Host (защита от Host header injection)
    # В test окружении TrustedHost отключён (через APP_ENV=development)
    if settings.APP_ENV == "production":
        app.add_middleware(TrustedHostMiddleware, allowed_hosts=settings.TRUSTED_HOSTS)

    # 3. CORS (для Flutter Web + Telegram Mini App)
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.CORS_ORIGINS,
        allow_credentials=settings.CORS_ALLOW_CREDENTIALS,
        allow_methods=["GET", "POST", "PUT", "DELETE", "PATCH", "OPTIONS"],
        allow_headers=["Authorization", "Content-Type", "X-Requested-With"],
        max_age=600,
    )

    # === Routers (Фаза 1) ===
    # from app.api import auth, keys, payments, servers, me
    # app.include_router(auth.router, prefix="/api/auth", tags=["auth"])
    # app.include_router(me.router, prefix="/api", tags=["me"])
    # app.include_router(keys.router, prefix="/api", tags=["keys"])
    # app.include_router(payments.router, prefix="/api", tags=["payments"])
    # app.include_router(servers.router, prefix="/api", tags=["servers"])

    # === Global exception handler ===
    @app.exception_handler(Exception)
    async def unhandled_exception_handler(request: Request, exc: Exception):
        log.error(
            "unhandled_exception",
            path=request.url.path,
            method=request.method,
            error=str(exc),
            exc_info=True,
        )
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={
                "detail": "Internal server error",
                "type": exc.__class__.__name__,
            },
        )

    # === Health check (обязательно для Docker HEALTHCHECK) ===
    @app.get("/health", tags=["meta"])
    async def health() -> dict:
        """Liveness probe — process alive."""
        return {
            "status": "ok",
            "app": settings.APP_NAME,
            "version": __version__,
            "env": settings.APP_ENV,
        }

    @app.get("/health/ready", tags=["meta"])
    async def readiness() -> dict:
        """Readiness probe — DB reachable."""
        checks = {"app": "ok", "database": "unknown"}
        try:
            from app.db.session import async_session_factory

            async with async_session_factory() as session:
                await session.execute(text("SELECT 1"))
            checks["database"] = "ok"
        except Exception as e:
            checks["database"] = f"error: {type(e).__name__}"
            return JSONResponse(status_code=503, content=checks)
        return checks

    # === Prometheus metrics ===
    if settings.PROMETHEUS_ENABLED:
        from prometheus_client import CONTENT_TYPE_LATEST, generate_latest

        @app.get("/metrics", tags=["meta"], include_in_schema=False)
        async def metrics():
            return JSONResponse(
                content=generate_latest().decode(),
                media_type=CONTENT_TYPE_LATEST,
            )

    # === Root ===
    @app.get("/", tags=["meta"])
    async def root() -> dict:
        return {
            "service": settings.APP_NAME,
            "version": __version__,
            "docs": "/docs",
            "health": "/health",
        }

    return app


app = create_app()
