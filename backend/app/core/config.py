"""
Application configuration via Pydantic Settings.

Loads from .env file. All secrets MUST be in .env, never in code.
"""
from functools import lru_cache
from typing import Literal

from pydantic import Field, PostgresDsn, RedisDsn, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=True,
        extra="ignore",
    )

    # === Application ===
    APP_NAME: str = "MAX VPS"
    APP_ENV: Literal["development", "staging", "production"] = "production"
    DEBUG: bool = False
    LOG_LEVEL: Literal["DEBUG", "INFO", "WARNING", "ERROR"] = "INFO"

    # === Server ===
    HOST: str = "0.0.0.0"
    PORT: int = 8000
    WORKERS: int = 2

    # === Database ===
    POSTGRES_HOST: str = "postgres"
    POSTGRES_PORT: int = 5432
    POSTGRES_DB: str = "maxvps"
    POSTGRES_USER: str = "maxvps"
    POSTGRES_PASSWORD: str = ""

    @property
    def DATABASE_URL(self) -> str:
        """Async PostgreSQL URL (asyncpg driver)."""
        return (
            f"postgresql+asyncpg://{self.POSTGRES_USER}:"
            f"{self.POSTGRES_PASSWORD}@{self.POSTGRES_HOST}:"
            f"{self.POSTGRES_PORT}/{self.POSTGRES_DB}"
        )

    @property
    def DATABASE_URL_SYNC(self) -> str:
        """Sync URL для Alembic миграций."""
        return (
            f"postgresql://{self.POSTGRES_USER}:"
            f"{self.POSTGRES_PASSWORD}@{self.POSTGRES_HOST}:"
            f"{self.POSTGRES_PORT}/{self.POSTGRES_DB}"
        )

    # === JWT ===
    JWT_SECRET_KEY: str = ""
    JWT_ALGORITHM: str = "HS256"
    JWT_ACCESS_TOKEN_EXPIRE_MINUTES: int = 15
    JWT_REFRESH_TOKEN_EXPIRE_DAYS: int = 7
    JWT_ISSUER: str = "maxvps.online"
    JWT_AUDIENCE: str = "maxvps-web"

    # === Telegram ===
    TG_BOT_TOKEN: str = ""
    BACKEND_URL: str = "https://maxvps.online"
    WEBAPP_URL: str = "https://maxvps.online/app/"

    # === CORS ===
    CORS_ORIGINS: list[str] = Field(
        default_factory=lambda: [
            "https://maxvps.online",
            "https://www.maxvps.online",
            "http://localhost:3000",  # Flutter Web dev
        ]
    )
    CORS_ALLOW_CREDENTIALS: bool = True

    # === Redis ===
    REDIS_HOST: str = "redis"
    REDIS_PORT: int = 6379
    REDIS_DB: int = 0
    REDIS_PASSWORD: str = ""

    @property
    def REDIS_URL(self) -> str:
        if self.REDIS_PASSWORD:
            return f"redis://:{self.REDIS_PASSWORD}@{self.REDIS_HOST}:{self.REDIS_PORT}/{self.REDIS_DB}"
        return f"redis://{self.REDIS_HOST}:{self.REDIS_PORT}/{self.REDIS_DB}"

    # === Rate limiting ===
    RATE_LIMIT_PER_MINUTE_AUTH: int = 5
    RATE_LIMIT_PER_MINUTE_API: int = 60
    RATE_LIMIT_PER_MINUTE_PAY: int = 10

    # === Auth codes ===
    AUTH_CODE_TTL_SECONDS: int = 300  # 5 минут
    AUTH_CODE_LENGTH: int = 6

    # === Webhook ===
    PUBLIC_WEBHOOK_BASE: str = "https://maxvps.online"

    # === Business ===
    MONTH_COST: str = "15000,39000,80000,160000"  # копейки
    TRIAL_PERIOD_DAYS: int = 1
    TRIAL_LIMIT_GB: int = 2
    LIMIT_IP: int = 5
    LIMIT_GB: int = 500
    REFERRAL_PERCENT: int = 20
    REFERRAL_MIN_WITHDRAWAL: int = 500

    @property
    def month_costs_list(self) -> list[int]:
        return [int(x) for x in self.MONTH_COST.split(",")]

    # === Security ===
    SECRET_KEY: str = ""
    TRUSTED_HOSTS: list[str] = Field(
        default_factory=lambda: ["maxvps.online", "www.maxvps.online", "localhost"]
    )

    # === Monitoring ===
    SENTRY_DSN: str = ""
    PROMETHEUS_ENABLED: bool = True

    @field_validator("JWT_SECRET_KEY")
    @classmethod
    def jwt_secret_not_empty(cls, v: str, info) -> str:
        if not v or len(v) < 32:
            raise ValueError(
                "JWT_SECRET_KEY must be at least 32 chars. "
                "Generate via: python3 -c \"import secrets; print(secrets.token_urlsafe(64))\""
            )
        return v


@lru_cache
def get_settings() -> Settings:
    """Cached settings singleton."""
    return Settings()


settings = get_settings()
