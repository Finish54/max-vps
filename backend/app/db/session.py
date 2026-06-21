"""
Database session management.

Provides:
- async_engine — singleton SQLAlchemy engine
- async_session_factory — sessionmaker
- get_db — FastAPI dependency
"""
from typing import AsyncIterator

from sqlalchemy.ext.asyncio import (
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)
from sqlalchemy.orm import DeclarativeBase

from app.core.config import settings


class Base(DeclarativeBase):
    """Base for all ORM models."""


# === Singleton engine ===
engine = create_async_engine(
    settings.DATABASE_URL,
    echo=settings.DEBUG,
    pool_size=10,
    max_overflow=20,
    pool_pre_ping=True,  # проверять соединение перед использованием
    pool_recycle=3600,  # пересоздавать соединения каждый час
)

# === Session factory ===
async_session_factory: async_sessionmaker[AsyncSession] = async_sessionmaker(
    engine,
    expire_on_commit=False,
    autoflush=False,
)


# === FastAPI dependency ===
async def get_db() -> AsyncIterator[AsyncSession]:
    """
    FastAPI dependency: yields AsyncSession, auto-closes.

    Usage:
        @app.get("/items")
        async def list_items(db: AsyncSession = Depends(get_db)):
            ...
    """
    async with async_session_factory() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()
