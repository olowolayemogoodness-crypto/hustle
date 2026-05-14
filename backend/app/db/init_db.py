import logging
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncEngine
import app.db.models  # noqa: F401
from app.db.models.base import Base
from app.db.session import engine as _engine

engine: AsyncEngine = _engine
logger = logging.getLogger(__name__)


async def test_connection():
    async with engine.begin() as conn:
        result = await conn.execute(text("SELECT 1"))
        logger.info("Database connection successful: %s", result.scalar())


async def init_models():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
        logger.info("ORM model metadata validated against the database.")
