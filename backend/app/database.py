"""Configuración de base de datos asíncrona con SQLAlchemy y persistencia real."""

import logging
from typing import Optional
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from sqlalchemy.orm import DeclarativeBase
from sqlalchemy import text
from app.config import settings

logger = logging.getLogger(__name__)


class Base(DeclarativeBase):
    """Clase base para todos los modelos ORM de SQLAlchemy."""
    pass


engine = None
async_session_factory = None


def create_engine_and_factory(db_url: str):
    """Crea un motor asíncrono y su fábrica de sesiones."""
    is_sqlite = "sqlite" in db_url
    eng = create_async_engine(
        db_url,
        echo=False,
        **(
            {"connect_args": {"check_same_thread": False}}
            if is_sqlite
            else {"pool_size": 10, "max_overflow": 20, "pool_pre_ping": True}
        ),
    )
    factory = async_sessionmaker(
        eng,
        class_=AsyncSession,
        expire_on_commit=False,
    )
    return eng, factory


# Configuración inicial con la URL de configuración o SQLite local persistente
primary_url = settings.async_database_url
try:
    if "postgresql" in primary_url:
        import asyncpg
    engine, async_session_factory = create_engine_and_factory(primary_url)
except (ImportError, ModuleNotFoundError, Exception) as exc:
    logger.info("Driver postgresql/asyncpg no disponible localmente (%s). Usando SQLite persistente.", exc)
    fallback_url = "sqlite+aiosqlite:///./altoque.db"
    engine, async_session_factory = create_engine_and_factory(fallback_url)


async def init_database():
    """Inicializa la base de datos, valida la conectividad y crea todas las tablas reales."""
    global engine, async_session_factory
    import app.models  # Importa todos los modelos ORM para registrarlos en Base.metadata

    try:
        async with engine.begin() as conn:
            await conn.execute(text("SELECT 1"))
            await conn.run_sync(Base.metadata.create_all)
        logger.info("Tablas de base de datos creadas/verificadas exitosamente.")
    except Exception as exc:
        logger.warning("Error al inicializar con motor principal (%s). Cambiando a SQLite persistente ./altoque.db", exc)
        fallback_url = "sqlite+aiosqlite:///./altoque.db"
        engine, async_session_factory = create_engine_and_factory(fallback_url)
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
        logger.info("Base de datos SQLite persistente inicializada correctamente en ./altoque.db")


async def get_db():
    """Inyector de sesión asíncrona por petición HTTP."""
    async with async_session_factory() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()
