from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models.match_log import MatchLog
from app.services.uuid_utils import parse_uuid, split_match_log_id


async def update_match_status(
    session: AsyncSession,
    match_log_id: str,
    status: str,
    accepted: bool | None = None,
) -> MatchLog | None:
    """
    Update match status without rejection semantics.
    Status can be: ranked, viewed, selected, archived
    """
    match_log = None
    try:
        match_log = await session.get(MatchLog, parse_uuid(match_log_id))
    except Exception:
        match_log = None

    # If not found by ID, try to find by job_id-worker_id composite key
    if match_log is None:
        try:
            job_id_str, worker_id_str = split_match_log_id(match_log_id)
            job_id_uuid = parse_uuid(job_id_str)
            worker_id_uuid = parse_uuid(worker_id_str)
            stmt = (
                select(MatchLog)
                .where(MatchLog.job_id == job_id_uuid)
                .where(MatchLog.worker_id == worker_id_uuid)
                .limit(1)
            )
            result = await session.execute(stmt)
            match_log = result.scalar_one_or_none()
        except Exception:
            pass

    if match_log is None:
        return None

    match_log.status = status
    if accepted is not None:
        match_log.accepted = accepted
    await session.commit()
    return match_log
