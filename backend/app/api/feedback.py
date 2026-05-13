from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import settings
from app.core.logging import get_logger
from app.db.deps import get_db
from app.schemas.feedback import FeedbackRequest, FeedbackResponse
from app.services.feedback_service import record_match_feedback

logger = get_logger(__name__)
router = APIRouter(prefix=f"{settings.api_prefix}/feedback", tags=["feedback"])


@router.post("/", response_model=FeedbackResponse)
async def submit_feedback(
    payload: FeedbackRequest,
    db: AsyncSession = Depends(get_db),
) -> FeedbackResponse:
    try:
        match_log, worker_trust = await record_match_feedback(
            session=db,
            match_log_id=payload.match_log_id,
            completed=payload.completed,
            dispute_occurred=payload.dispute_occurred,
            employer_rating=payload.employer_rating,
            worker_rating=payload.worker_rating,
        )

        if match_log is None:
            raise HTTPException(status_code=404, detail="Match log entry not found")

        return FeedbackResponse(
            match_log_id=str(match_log.id),
            completed=match_log.completed,
            dispute_occurred=match_log.dispute_occurred,
            employer_rating=match_log.employer_rating,
            worker_rating=match_log.worker_rating,
            worker_updated_trust=worker_trust,
        )
    except HTTPException:
        raise
    except Exception as err:
        logger.error("Failed to record feedback: %s", err, exc_info=True)
        raise HTTPException(status_code=500, detail="Failed to record feedback")
