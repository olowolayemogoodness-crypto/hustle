"""Dependency injection for repository layer."""

from typing import AsyncGenerator
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.repositories.unit_of_work import UnitOfWork
from app.db.session import AsyncSessionLocal


async def get_unit_of_work() -> AsyncGenerator[UnitOfWork, None]:
    """Provide UnitOfWork instance for dependency injection.
    
    Usage in FastAPI route:
        @router.post("/api/endpoint")
        async def my_endpoint(uow: UnitOfWork = Depends(get_unit_of_work)):
            async with uow:
                match_logs = await uow.match_logs.list_all()
                await uow.commit()
    """
    session = AsyncSessionLocal()
    uow = UnitOfWork(session)
    try:
        yield uow
    finally:
        await uow.close()
