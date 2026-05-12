import asyncio

from app.db.init_db import test_connection


asyncio.run(test_connection())