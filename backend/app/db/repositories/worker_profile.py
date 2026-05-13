"""Worker profile repository."""

from typing import Optional
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from uuid import UUID

from app.db.models.worker_profile import WorkerProfile
from app.db.repositories.base import BaseRepository


class WorkerProfileRepository(BaseRepository[WorkerProfile]):
    """Repository for worker profile operations."""

    def __init__(self, session: AsyncSession):
        super().__init__(session, WorkerProfile)

    async def get_by_user_id(self, user_id: UUID) -> Optional[WorkerProfile]:
        """Get worker profile by user ID."""
        stmt = select(WorkerProfile).where(WorkerProfile.user_id == user_id)
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def get_verified_workers(self) -> list[WorkerProfile]:
        """Get all verified workers."""
        stmt = select(WorkerProfile).where(WorkerProfile.verified == True)
        result = await self.session.execute(stmt)
        return result.scalars().all()
