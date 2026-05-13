"""Unit of Work pattern for transaction management."""

from typing import Optional
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.repositories.match_log import MatchLogRepository
from app.db.repositories.job import JobRepository
from app.db.repositories.worker_profile import WorkerProfileRepository


class UnitOfWork:
    """
    Unit of Work pattern for managing transactions and coordinating repositories.
    
    Ensures all repositories share the same session and transaction context.
    """

    def __init__(self, session: AsyncSession):
        self.session = session
        self._match_logs: Optional[MatchLogRepository] = None
        self._jobs: Optional[JobRepository] = None
        self._worker_profiles: Optional[WorkerProfileRepository] = None

    @property
    def match_logs(self) -> MatchLogRepository:
        """Lazy-load match log repository."""
        if self._match_logs is None:
            self._match_logs = MatchLogRepository(self.session)
        return self._match_logs

    @property
    def jobs(self) -> JobRepository:
        """Lazy-load job repository."""
        if self._jobs is None:
            self._jobs = JobRepository(self.session)
        return self._jobs

    @property
    def worker_profiles(self) -> WorkerProfileRepository:
        """Lazy-load worker profile repository."""
        if self._worker_profiles is None:
            self._worker_profiles = WorkerProfileRepository(self.session)
        return self._worker_profiles

    async def commit(self) -> None:
        """Commit the current transaction."""
        await self.session.commit()

    async def rollback(self) -> None:
        """Rollback the current transaction."""
        await self.session.rollback()

    async def flush(self) -> None:
        """Flush pending changes to the database without committing."""
        await self.session.flush()

    async def close(self) -> None:
        """Close the session."""
        await self.session.close()

    async def __aenter__(self) -> "UnitOfWork":
        """Async context manager entry."""
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb) -> None:
        """Async context manager exit with automatic rollback on error."""
        if exc_type is not None:
            await self.rollback()
        else:
            await self.commit()
        await self.close()
