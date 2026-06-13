"""Конфигурация и управление подключением к PostgreSQL"""

from typing import Any, AsyncGenerator

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.orm import DeclarativeBase

from core.config import settings

engine = create_async_engine(url=settings.database_url)

AsyncSessionLocal = async_sessionmaker(
    bind=engine,
    expire_on_commit=False,
    autoflush=False,
)


class Base(DeclarativeBase):
    """Базовый класс для всех моделей SQLAlchemy"""

    pass


async def get_db() -> AsyncGenerator[AsyncSession, Any]:
    """Получить сессию базы данных"""
    async with AsyncSessionLocal() as session:
        yield session
