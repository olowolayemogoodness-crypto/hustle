from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.core.logging import get_logger
from app.db.deps import get_db
from app.db.models.match_log import MatchLog
from app.schemas.match import (
    MatchRequest,
    MatchResponse,
    AcceptMatchRequest,
    AcceptMatchResponse,
    MatchHistoryEntry,
    MatchHistoryResponse,
    MatchStatusUpdate,
    MatchStatusResponse,
)
from app.services.matching_engine import rank_candidates
from app.services.event_logger import worker_scores_to_events, persist_match_events
from app.services.match_status_service import update_match_status

logger = get_logger(__name__)
router = APIRouter(prefix=settings.api_prefix, tags=["match"])


def select_recommended_workers(ranked_workers, max_recommended: int = 3):
    """Select top N recommended workers from ranked score results."""
    return [worker.worker_id for worker in ranked_workers[:max_recommended]]


@router.post("/match", response_model=MatchResponse)
async def match(
    payload: MatchRequest,
    db: AsyncSession = Depends(get_db),
):
    """
    Main matching endpoint: rank workers and recommend selections.
    
    Flow:
    1. Pure ranking (no side effects)
    2. Decision (select top workers)
    3. Event logging (decoupled, won't break API)
    4. Return response
    """
    logger.info("Matching job=%s against %d workers", payload.job.id, len(payload.workers))
    
    # Step 1: Rank candidates (pure function)
    ranked = rank_candidates(payload.job, payload.workers)
    logger.info("Ranked %d workers for job=%s", len(ranked), payload.job.id)
    
    # Step 2: Select recommended workers
    recommended_ids = select_recommended_workers(ranked, max_recommended=3)
    
    # Step 3: Log events (decoupled from ranking)
    try:
        events = worker_scores_to_events(payload.job.id, ranked)
        persisted = await persist_match_events(db, events)
        logger.info("Persisted %d match events for job=%s", persisted, payload.job.id)
    except SQLAlchemyError as err:
        logger.error("Failed to log match events: %s", err, exc_info=True)
        # Continue — logging failure should not break the API response
    
    # Step 4: Return response
    top_ranked = ranked[:10]
    return MatchResponse(
        job_id=str(payload.job.id),
        ranked_workers=top_ranked,
        recommended_worker_ids=recommended_ids,
    )


@router.post("/match/accept", response_model=AcceptMatchResponse)
async def accept_match(
    payload: AcceptMatchRequest,
    db: AsyncSession = Depends(get_db),
):
    logger.info("Accepting match for job=%s, worker=%s", payload.job_id, payload.worker_id)
    match_log_id = f"{payload.job_id}-{payload.worker_id}"
    match_log = await update_match_status(
        db,
        match_log_id,
        status="selected",
        accepted=True,
    )

    if match_log is None:
        raise HTTPException(status_code=404, detail="Match log entry not found")

    return AcceptMatchResponse(
        match_log_id=str(match_log.id),
        accepted=True,
    )


@router.post("/match/status", response_model=MatchStatusResponse)
async def update_match_state(
    payload: MatchStatusUpdate,
    db: AsyncSession = Depends(get_db),
):
    """
    Update match status: viewed → employer saw the candidate, selected → chosen.
    No rejection semantics — just state tracking.
    """
    logger.info("Updating match %s status to %s", payload.match_log_id, payload.status)
    match_log = await update_match_status(db, payload.match_log_id, payload.status)
    if match_log is None:
        raise HTTPException(status_code=404, detail="Match log entry not found")

    return MatchStatusResponse(
        match_log_id=str(match_log.id),
        status=payload.status,
        message=f"Match marked as {payload.status}",
    )


@router.get("/match/history/{job_id}", response_model=MatchHistoryResponse)
async def get_match_history(
    job_id: str,
    db: AsyncSession = Depends(get_db),
):
    logger.info("Retrieving match history for job=%s", job_id)
    from app.services.uuid_utils import parse_uuid

    try:
        parsed_job_id = parse_uuid(job_id)
    except (TypeError, ValueError):
        raise HTTPException(status_code=400, detail="Invalid job_id format")

    stmt = select(MatchLog).where(MatchLog.job_id == parsed_job_id).order_by(MatchLog.created_at.desc())
    result = await db.execute(stmt)
    logs = result.scalars().all()

    history_entries = [
        MatchHistoryEntry(
            worker_id=str(log.worker_id),
            final_score=log.final_score,
            rule_score=log.rule_score,
            ml_probability=log.ml_probability,
            risk_penalty=log.risk_penalty,
            confidence=log.confidence,
            status=log.status,
            accepted=log.accepted,
            completed=log.completed,
            dispute_occurred=log.dispute_occurred,
            employer_rating=log.employer_rating,
            worker_rating=log.worker_rating,
            completion_risk_probability=log.completion_risk_probability,
            risk_factors=log.risk_factors,
            created_at=str(log.created_at) if log.created_at else None,
            updated_at=str(log.updated_at) if log.updated_at else None,
        )
        for log in logs
    ]

    return MatchHistoryResponse(
        job_id=str(parsed_job_id) if parsed_job_id is not None else str(job_id),
        matches=history_entries,
    )
