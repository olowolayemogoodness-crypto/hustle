import os
from pathlib import Path
import asyncio

import pytest
from fastapi.testclient import TestClient
from sqlalchemy.ext.asyncio import AsyncSession

TEST_DB_PATH = Path(__file__).resolve().parent / "test_hustle.db"
os.environ["HUSTLE_DATABASE_URL"] = f"sqlite+aiosqlite:///{TEST_DB_PATH.as_posix()}"
os.environ["HUSTLE_TESTING"] = "1"

from app.db.session import AsyncSessionLocal
from app.db.init_db import init_models
from app.db.deps import get_db
from app.main import app


@pytest.fixture(scope="session", autouse=True)
def init_test_db():
    """Initialize database schema once per test session."""
    if TEST_DB_PATH.exists():
        try:
            TEST_DB_PATH.unlink(missing_ok=True)
        except PermissionError:
            # If the test database file is locked by another process, leave it in place.
            pass
    asyncio.run(init_models())


@pytest.fixture
def client():
    """FastAPI test client fixture with session commit override."""
    async def override_get_db():
        session = AsyncSessionLocal()
        try:
            yield session
        finally:
            await session.commit()
            await session.close()

    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides = {}


@pytest.fixture
async def db_session():
    """Async database session fixture."""
    async with AsyncSessionLocal() as session:
        yield session