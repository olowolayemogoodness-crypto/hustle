from sqlalchemy import text

from app.db.models.base import Base
from app.db.session import engine


async def test_connection():
    async with engine.begin() as conn:
        result = await conn.execute(text("SELECT 1"))
        print("Database connection successful:", result.scalar())


async def init_models():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
        print("ORM model metadata validated against the database.")