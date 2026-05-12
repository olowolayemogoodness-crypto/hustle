import pytest

from app.db.init_db import test_connection


@pytest.mark.asyncio
async def test_database_connection():
    await test_connection()