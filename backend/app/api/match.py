from fastapi import APIRouter
from app.config import settings
from app.core.logging import get_logger
from app.schemas.match import MatchRequest, MatchResponse
from app.services.matching_service import match_workers

logger = get_logger(__name__)
router = APIRouter(prefix=settings.api_prefix, tags=["match"])

@router.post("/match", response_model=MatchResponse)
def match(payload: MatchRequest):
    logger.info("Received /match request for job=%s and %d workers", payload.job.id, len(payload.workers))
    results = match_workers(payload.job, payload.workers)
    return {"matches": results[:10]}
