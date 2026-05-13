"""MatchLog repository."""

from typing import List, Optional
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from uuid import UUID

from app.db.models.match_log import MatchLog
from app.db.repositories.base import BaseRepository


class MatchLogRepository(BaseRepository[MatchLog]):
    """Repository for match log operations."""

    def __init__(self, session: AsyncSession):
        super().__init__(session, MatchLog)

    async def get_by_job_id(self, job_id: UUID) -> List[MatchLog]:
        """Get all match logs for a job."""
        stmt = select(MatchLog).where(MatchLog.job_id == job_id).order_by(MatchLog.created_at.desc())
        result = await self.session.execute(stmt)
        return result.scalars().all()

    async def get_by_worker_id(self, worker_id: UUID) -> List[MatchLog]:
        """Get all match logs for a worker."""
        stmt = select(MatchLog).where(MatchLog.worker_id == worker_id).order_by(MatchLog.created_at.desc())
        result = await self.session.execute(stmt)
        return result.scalars().all()

    async def get_by_job_and_worker(self, job_id: UUID, worker_id: UUID) -> Optional[MatchLog]:
        """Get match log for a specific job-worker pair."""
        stmt = select(MatchLog).where(
            (MatchLog.job_id == job_id) & (MatchLog.worker_id == worker_id)
        )
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def get_accepted_matches(self, job_id: UUID) -> List[MatchLog]:
        """Get accepted matches for a job."""
        stmt = select(MatchLog).where(
            (MatchLog.job_id == job_id) & (MatchLog.accepted == True)
        ).order_by(MatchLog.updated_at.desc())
        result = await self.session.execute(stmt)
        return result.scalars().all()

    async def get_top_matches(self, job_id: UUID, limit: int = 10) -> List[MatchLog]:
        """Get top-scored matches for a job."""
        stmt = select(MatchLog).where(
            MatchLog.job_id == job_id
        ).order_by(MatchLog.final_score.desc()).limit(limit)
        result = await self.session.execute(stmt)
        return result.scalars().all()
