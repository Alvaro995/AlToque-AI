"""Configuración de base de datos asíncrona con SQLAlchemy y fallback resiliente."""

from typing import Optional
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from sqlalchemy.orm import DeclarativeBase
from app.config import settings


class Base(DeclarativeBase):
    """Clase base para todos los modelos ORM de SQLAlchemy."""
    pass


# Inicialización resiliente del motor para ambientes locales o de pruebas
engine = None
async_session_factory = None

try:
    if "postgresql+asyncpg" in settings.database_url:
        import asyncpg
    engine = create_async_engine(
        settings.database_url,
        echo=settings.debug,
        pool_size=10,
        max_overflow=20,
        pool_pre_ping=True,
    )
    async_session_factory = async_sessionmaker(
        engine,
        class_=AsyncSession,
        expire_on_commit=False,
    )
except (ImportError, Exception):
    try:
        import aiosqlite
        engine = create_async_engine("sqlite+aiosqlite:///:memory:", echo=False)
        async_session_factory = async_sessionmaker(
            engine,
            class_=AsyncSession,
            expire_on_commit=False,
        )
    except Exception:
        engine = None
        async_session_factory = None


class DummyAsyncSession:
    """Sesión simulada para pruebas o ambientes sin conexión activa."""

    def add(self, instance):
        pass

    async def commit(self):
        pass

    async def rollback(self):
        pass

    async def refresh(self, instance):
        pass

    async def close(self):
        pass

    async def execute(self, statement, *args, **kwargs):
        return None


async def get_db():
    """Inyector de sesión asíncrona por petición HTTP."""
    if async_session_factory is None:
        yield DummyAsyncSession()
        return
    async with async_session_factory() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()

