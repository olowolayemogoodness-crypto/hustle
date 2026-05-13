import os
from typing import AsyncGenerator

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.pool import NullPool

from app.config import settings


def _is_sqlite(url: str) -> bool:
    return url.startswith(("sqlite", "sqlite+"))


def _is_test_mode() -> bool:
    return bool(os.getenv("PYTEST_CURRENT_TEST") or os.getenv("HUSTLE_TESTING") or settings.testing)


def _build_engine_kwargs(database_url: str) -> dict[str, object]:
    kwargs: dict[str, object] = {
        "echo": settings.debug,
        "future": True,
        "pool_pre_ping": True,
    }

    if _is_sqlite(database_url):
        kwargs["connect_args"] = {"check_same_thread": False}

    if _is_test_mode():
        kwargs["poolclass"] = NullPool
    elif not _is_sqlite(database_url):
        kwargs.update(
            {
                "pool_size": settings.db_pool_size,
                "max_overflow": settings.db_max_overflow,
                "pool_timeout": settings.db_pool_timeout,
                "pool_recycle": settings.db_pool_recycle,
            }
        )

    return kwargs


def create_engine(database_url: str | None = None, **overrides) -> object:
    target_url = database_url or settings.database_url
    kwargs = _build_engine_kwargs(target_url)
    kwargs.update(overrides)
    return create_async_engine(target_url, **kwargs)


engine = create_engine()

AsyncSessionLocal = async_sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False,
)


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """FastAPI dependency for database sessions."""
    async with AsyncSessionLocal() as session:
        yield session