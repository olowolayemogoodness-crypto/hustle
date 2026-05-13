from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app import config
from app.db.models.match_log import MatchLog
from app.db.models.worker_profile import WorkerProfile
from app.services.uuid_utils import parse_uuid, split_match_log_id


async def update_worker_feedback(
    session: AsyncSession,
    worker_id: UUID | str,
    completed: bool,
    dispute_occurred: bool,
    worker_rating: float | None,
) -> WorkerProfile | None:
    try:
        worker_uuid = parse_uuid(worker_id)
    except (TypeError, ValueError):
        return None

    statement = select(WorkerProfile).where(WorkerProfile.user_id == worker_uuid)
    result = await session.execute(statement)
    profile = result.scalar_one_or_none()

    if profile is None:
        return None

    existing_total = profile.total_jobs or 0
    existing_rating = profile.avg_rating or 0.0
    existing_completion = profile.completion_rate or config.settings.fallback_probability

    updated_total = existing_total
    if worker_rating is not None:
        updated_total += 1
        profile.avg_rating = (
            (existing_rating * existing_total) + worker_rating
        ) / updated_total
        profile.total_jobs = updated_total

    if completed:
        profile.completion_rate = min(
            1.0,
            ((existing_completion * existing_total) + 1.0) / max(1, updated_total),
        )
    elif updated_total > 0:
        profile.completion_rate = min(
            1.0,
            ((existing_completion * existing_total) + 0.0) / updated_total,
        )

    if dispute_occurred:
        profile.disputes_count = (profile.disputes_count or 0) + 1

    profile.trust_score = min(
        1.0,
        0.35 * (profile.avg_rating / 5 if profile.avg_rating else 0.0)
        + 0.45 * profile.completion_rate
        + 0.20 * (1 - min((profile.disputes_count or 0) / 10, 1.0)),
    )

    return profile


async def record_match_feedback(
    session: AsyncSession,
    match_log_id: str,
    completed: bool,
    dispute_occurred: bool = False,
    employer_rating: float | None = None,
    worker_rating: float | None = None,
) -> tuple[MatchLog | None, float | None]:
    match_log = None
    match_log_uuid = None
    try:
        match_log_uuid = parse_uuid(match_log_id)
    except (TypeError, ValueError):
        match_log_uuid = None

    if match_log_uuid is not None:
        match_log = await session.get(MatchLog, match_log_uuid)

    if match_log is None:
        try:
            job_id_str, worker_id_str = split_match_log_id(match_log_id)
            job_id_uuid = parse_uuid(job_id_str)
            worker_id_uuid = parse_uuid(worker_id_str)
            statement = (
                select(MatchLog)
                .where(MatchLog.job_id == job_id_uuid)
                .where(MatchLog.worker_id == worker_id_uuid)
                .order_by(MatchLog.created_at.desc())
                .limit(1)
            )
            result = await session.execute(statement)
            match_log = result.scalar_one_or_none()
        except (ValueError, AttributeError, TypeError):
            match_log = None

    if match_log is None:
        return None, None

    match_log.completed = completed
    match_log.dispute_occurred = dispute_occurred
    match_log.employer_rating = employer_rating
    match_log.worker_rating = worker_rating
    match_log.accepted = True

    profile = await update_worker_feedback(
        session=session,
        worker_id=match_log.worker_id,
        completed=completed,
        dispute_occurred=dispute_occurred,
        worker_rating=worker_rating,
    )

    await session.commit()
    return match_log, profile.trust_score if profile is not None else None
