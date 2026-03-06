"""SQLAlchemy async database connection and session management."""

import logging
from typing import AsyncGenerator

from sqlalchemy import text
from sqlalchemy.ext.asyncio import (
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)
from sqlalchemy.orm import DeclarativeBase

from app.config import settings

logger = logging.getLogger(__name__)


def _make_async_url(url: str) -> str:
    """Convert a sync postgresql URL to an async (asyncpg) URL."""
    if url.startswith("postgresql://"):
        return url.replace("postgresql://", "postgresql+asyncpg://", 1)
    if url.startswith("postgres://"):
        return url.replace("postgres://", "postgresql+asyncpg://", 1)
    return url


def _create_engine_and_session():
    """Lazily create the engine and session factory."""
    db_url = _make_async_url(settings.DATABASE_URL)

    # aiosqlite-based SQLite URLs don't support pool_size / max_overflow
    _is_sqlite = db_url.startswith("sqlite")
    kwargs = {} if _is_sqlite else {"pool_pre_ping": True, "pool_size": 10, "max_overflow": 20}

    _engine = create_async_engine(
        db_url,
        echo=(settings.ENVIRONMENT == "development"),
        **kwargs,
    )
    _session = async_sessionmaker(
        bind=_engine,
        class_=AsyncSession,
        expire_on_commit=False,
        autoflush=False,
        autocommit=False,
    )
    return _engine, _session


# Defer engine creation until first access so imports in test environments
# that override DATABASE_URL work correctly.
_engine_instance = None
_session_instance = None


def _get_engine():
    global _engine_instance, _session_instance
    if _engine_instance is None:
        _engine_instance, _session_instance = _create_engine_and_session()
    return _engine_instance


def _get_session():
    global _engine_instance, _session_instance
    if _session_instance is None:
        _engine_instance, _session_instance = _create_engine_and_session()
    return _session_instance


# Public aliases – accessed as engine / AsyncSessionLocal throughout the codebase
class _LazyEngine:
    def __getattr__(self, name):
        return getattr(_get_engine(), name)

    def begin(self):
        return _get_engine().begin()

    def connect(self):
        return _get_engine().connect()

    def dispose(self):
        return _get_engine().dispose()


class _LazySession:
    def __call__(self, *args, **kwargs):
        return _get_session()(*args, **kwargs)

    def __getattr__(self, name):
        return getattr(_get_session(), name)


engine = _LazyEngine()  # type: ignore[assignment]
AsyncSessionLocal = _LazySession()  # type: ignore[assignment]


class Base(DeclarativeBase):
    """Declarative base for all SQLAlchemy models."""
    pass


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """FastAPI dependency that provides a database session per request."""
    async with AsyncSessionLocal() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()


async def init_db() -> None:
    """Create pgvector extension and all tables on startup."""
    async with engine.begin() as conn:
        try:
            await conn.execute(text("CREATE EXTENSION IF NOT EXISTS vector"))
            logger.info("pgvector extension ensured.")
        except Exception as exc:
            logger.warning("Could not create pgvector extension: %s", exc)

        # Import all models so they register with Base.metadata
        from app.models import (  # noqa: F401
            audit_log,
            commitment,
            entity,
            feedback,
            goal,
            insight,
            memory,
            project,
            reminder,
            source_document,
            task,
            user,
        )

        await conn.run_sync(Base.metadata.create_all)
        logger.info("Database tables created / verified.")
