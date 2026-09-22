"""Test configuration.

We force a private in-memory SQLite database and a fixed secret BEFORE any app
module is imported, so the whole suite runs with zero external services.
"""
from __future__ import annotations

import os

os.environ["DATABASE_URL"] = "sqlite+aiosqlite://"
os.environ["SECRET_KEY"] = "test-secret-key-not-for-production"
os.environ["AUTH_RATE_LIMIT"] = "1000"
os.environ["REFRESH_COOKIE_SECURE"] = "false"
os.environ["ENV"] = "test"

import json  # noqa: E402
from pathlib import Path  # noqa: E402

import pytest  # noqa: E402
import pytest_asyncio  # noqa: E402
from httpx import ASGITransport, AsyncClient  # noqa: E402
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine  # noqa: E402
from sqlalchemy.pool import StaticPool  # noqa: E402

from app import models  # noqa: E402,F401  (registers tables)
from app.core.rate_limit import limiter  # noqa: E402
from app.core.security import hash_password  # noqa: E402
from app.db.base import Base  # noqa: E402
from app.db.session import get_db  # noqa: E402
from app.main import app  # noqa: E402
from app.models.user import User  # noqa: E402
from app.services.case_importer import import_case  # noqa: E402

CASE_001 = json.loads(
    (Path(__file__).resolve().parents[1] / "cases" / "case-001.json").read_text(encoding="utf-8")
)


@pytest_asyncio.fixture
async def db_engine():
    engine = create_async_engine(
        "sqlite+aiosqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield engine
    await engine.dispose()


@pytest.fixture
def session_factory(db_engine):
    return async_sessionmaker(db_engine, expire_on_commit=False, class_=AsyncSession)


@pytest_asyncio.fixture
async def client(db_engine, session_factory):
    async def _get_test_db():
        async with session_factory() as session:
            try:
                yield session
            except Exception:
                await session.rollback()
                raise

    app.dependency_overrides[get_db] = _get_test_db
    limiter.reset()
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as c:
        yield c
    app.dependency_overrides.clear()


@pytest_asyncio.fixture
async def imported_case(session_factory):
    """Import Case #001 into the test database and return its code."""
    async with session_factory() as session:
        await import_case(session, CASE_001)
        await session.commit()
    return CASE_001["code"]


@pytest_asyncio.fixture
async def admin_credentials(session_factory):
    creds = {"email": "admin@test.example", "password": "Admin#12345"}
    async with session_factory() as session:
        session.add(
            User(
                email=creds["email"],
                password_hash=hash_password(creds["password"]),
                role="ADMIN",
                display_name="Test Admin",
            )
        )
        await session.commit()
    return creds
