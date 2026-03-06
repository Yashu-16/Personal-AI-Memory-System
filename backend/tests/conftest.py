"""Pytest fixtures for the Memora backend test suite.

Uses SQLite (sync for table creation/data setup, async aiosqlite for the API).
"""

import os

# Must be set BEFORE importing any app module.
os.environ["DATABASE_URL"] = "sqlite+aiosqlite:///./test_memora.db"
os.environ.setdefault("SECRET_KEY", "test-secret-key-for-testing")

import uuid as _uuid_module

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import JSON, String, Text, create_engine
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy.types import TypeDecorator

from app.database import Base


# ---------------------------------------------------------------------------
# Portable UUID type for SQLite
# ---------------------------------------------------------------------------

class _SQLiteUUID(TypeDecorator):
    """Stores UUID as a 36-char string with dashes (compatible with both
    sync and async SQLite connections)."""

    impl = String(36)
    cache_ok = True

    def process_bind_param(self, value, dialect):
        if value is None:
            return None
        return str(value)  # uuid.UUID → "xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx"

    def process_result_value(self, value, dialect):
        if value is None:
            return None
        return _uuid_module.UUID(str(value))


# ---------------------------------------------------------------------------
# Sync engine (for table creation + data setup in fixtures)
# ---------------------------------------------------------------------------
_sync_engine = create_engine(
    "sqlite:///./test_memora.db",
    connect_args={"check_same_thread": False},
)
_SyncSession = sessionmaker(bind=_sync_engine, autoflush=False, autocommit=False)


def _create_tables() -> None:
    from app.models import (  # noqa: F401
        audit_log, commitment, entity, feedback, goal,
        insight, memory, project, reminder, source_document, task, user,
    )
    for table in Base.metadata.tables.values():
        for col in table.columns:
            t = col.type.__class__.__name__
            if t == "UUID":
                col.type = _SQLiteUUID()
            elif t == "Vector":
                col.type = Text()
            elif t == "JSONB":
                col.type = JSON()
    Base.metadata.create_all(_sync_engine)


_create_tables()

# ---------------------------------------------------------------------------
# Async engine (used by the FastAPI app via get_db override)
# ---------------------------------------------------------------------------
_async_engine = create_async_engine(
    "sqlite+aiosqlite:///./test_memora.db",
    connect_args={"check_same_thread": False},
)
_AsyncTestSession = async_sessionmaker(
    bind=_async_engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autoflush=False,
    autocommit=False,
)

# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------


@pytest.fixture(autouse=True)
def _clean_db():
    """Truncate all tables before each test."""
    with _sync_engine.begin() as conn:
        for table in reversed(Base.metadata.sorted_tables):
            conn.execute(table.delete())
    yield


@pytest.fixture()
def db():
    """Synchronous session for setting up test data."""
    session = _SyncSession()
    try:
        yield session
        session.commit()
    except Exception:
        session.rollback()
        raise
    finally:
        session.close()


@pytest.fixture()
def client():
    """TestClient with get_db overridden to use the async SQLite session."""
    from app.main import app
    from app.database import get_db

    async def _get_db_override():
        async with _AsyncTestSession() as session:
            try:
                yield session
                await session.commit()
            except Exception:
                await session.rollback()
                raise

    app.dependency_overrides[get_db] = _get_db_override
    with TestClient(app, raise_server_exceptions=True) as c:
        yield c
    app.dependency_overrides.clear()


@pytest.fixture()
def test_user(db):
    """Create and return a test User object."""
    from passlib.context import CryptContext

    from app.models.user import User

    pwd_ctx = CryptContext(schemes=["bcrypt"], deprecated="auto")
    user = User(
        email="testuser@example.com",
        hashed_password=pwd_ctx.hash("testpassword123"),
        full_name="Test User",
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


@pytest.fixture()
def auth_headers(test_user):
    """Authorization headers for the test user."""
    from app.api.auth import create_access_token

    token = create_access_token(str(test_user.id))
    return {"Authorization": f"Bearer {token}"}
