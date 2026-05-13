import os

from sqlalchemy.ext.asyncio import (
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)
from sqlalchemy.pool import NullPool

from app.config import settings

TESTING = os.getenv("PYTEST_CURRENT_TEST") is not None or os.getenv("HUSTLE_TESTING") == "1"
IS_SQLITE = settings.database_url.startswith("sqlite") or settings.database_url.startswith("sqlite+")

engine_kwargs = {
    "echo": settings.debug,
    "future": True,
    "pool_pre_ping": True,
}

if IS_SQLITE:
    engine_kwargs["connect_args"] = {
        "check_same_thread": False,
    }

if TESTING:
    engine_kwargs["poolclass"] = NullPool
elif not IS_SQLITE:
    engine_kwargs.update(
        {
            "pool_size": settings.db_pool_size,
            "max_overflow": settings.db_max_overflow,
            "pool_timeout": settings.db_pool_timeout,
            "pool_recycle": settings.db_pool_recycle,
        }
    )

engine = create_async_engine(settings.database_url, **engine_kwargs)


AsyncSessionLocal = async_sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False,
)


async def get_db():
    """
    FastAPI dependency for database sessions.
    """
    async with AsyncSessionLocal() as session:
        yield session