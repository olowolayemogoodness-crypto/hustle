"""Job repository."""

from typing import Optional
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from uuid import UUID

from app.db.models.job import Job
from app.db.repositories.base import BaseRepository


class JobRepository(BaseRepository[Job]):
    """Repository for job operations."""

    def __init__(self, session: AsyncSession):
        super().__init__(session, Job)

    async def get_by_title(self, title: str) -> Optional[Job]:
        """Get job by title."""
        stmt = select(Job).where(Job.title == title)
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def get_by_employer(self, employer_id: UUID) -> list[Job]:
        """Get all jobs for an employer."""
        stmt = select(Job).where(Job.employer_id == employer_id).order_by(Job.created_at.desc())
        result = await self.session.execute(stmt)
        return result.scalars().all()
