"""Tests for Settings (config loading + validation).

Используем monkeypatch + переменные окружения, не _env_file (Pydantic v2 изменил API).
"""
import pytest
from pydantic import ValidationError

from app.core.config import Settings


@pytest.fixture
def minimal_env(monkeypatch):
    """Set required env vars (JWT_SECRET_KEY + остальные имеют defaults)."""
    secret = "x" * 32  # 32 chars, passes validator
    monkeypatch.setenv("JWT_SECRET_KEY", secret)
    # Force reload
    from app.core import config as cfg_module
    cfg_module.get_settings.cache_clear()
    yield
    cfg_module.get_settings.cache_clear()


def test_default_settings(minimal_env):
    """Settings load with sane defaults."""
    s = Settings()
    assert s.APP_NAME == "MAX VPS"
    assert s.PORT == 8000
    assert s.JWT_ALGORITHM == "HS256"


def test_database_url_format(minimal_env):
    """DATABASE_URL is asyncpg-compatible."""
    s = Settings()
    assert "postgresql+asyncpg://" in s.DATABASE_URL
    assert s.POSTGRES_DB in s.DATABASE_URL


def test_jwt_secret_too_short():
    """JWT_SECRET_KEY shorter than 32 chars → ValidationError."""
    with pytest.raises(ValidationError) as exc_info:
        Settings(JWT_SECRET_KEY="tooshort")
    assert "JWT_SECRET_KEY" in str(exc_info.value)


def test_jwt_secret_valid(minimal_env):
    """Valid JWT_SECRET_KEY passes."""
    s = Settings()
    assert len(s.JWT_SECRET_KEY) == 32


def test_month_cost_parsing(minimal_env, monkeypatch):
    """MONTH_COST parses to list of ints."""
    monkeypatch.setenv("MONTH_COST", "100,200,300")
    from app.core import config as cfg_module
    cfg_module.get_settings.cache_clear()
    s = Settings()
    assert s.month_costs_list == [100, 200, 300]


def test_cors_origins_default():
    """Default CORS includes maxvps.online + localhost."""
    s = Settings(JWT_SECRET_KEY="x" * 32)
    assert "https://maxvps.online" in s.CORS_ORIGINS
    assert "http://localhost:3000" in s.CORS_ORIGINS


def test_database_url_sync_format():
    """DATABASE_URL_SYNC для Alembic (sync psycopg2)."""
    s = Settings(JWT_SECRET_KEY="x" * 32)
    assert "postgresql://" in s.DATABASE_URL_SYNC
    assert "asyncpg" not in s.DATABASE_URL_SYNC
