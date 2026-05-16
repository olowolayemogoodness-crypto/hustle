"""Analytics endpoint for match statistics."""
from fastapi import APIRouter, Depends
from pydantic import BaseModel, Field
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.core.logging import get_logger
from app.db.deps import get_db
from app.db.models.match_log import MatchLog

logger = get_logger(__name__)
router = APIRouter(prefix=f"{settings.api_prefix}/analytics", tags=["analytics"])


class AnalyticsResponse(BaseModel):
    """Response with match analytics."""
    total_matches: int = Field(default=0, ge=0, description="Total number of matches")
    average_match_score: float = Field(default=0.0, ge=0.0, le=1.0, description="Average match score")
    acceptance_rate: float = Field(default=0.0, ge=0.0, le=1.0, description="Acceptance rate")
    completed_matches: int = Field(default=0, ge=0, description="Number of completed matches")
    disputed_matches: int = Field(default=0, ge=0, description="Number of disputed matches")


@router.get("/matches", response_model=AnalyticsResponse)
async def get_match_analytics(db: AsyncSession = Depends(get_db)) -> AnalyticsResponse:
    """
    Get overall match analytics.
    
    Returns:
        - total_matches: Count of all ranked matches
        - average_match_score: Mean of all final scores
        - acceptance_rate: Ratio of accepted matches
        - completed_matches: Count of completed matches
        - disputed_matches: Count of matches with disputes
    """
    logger.info("Retrieving match analytics")
    
    try:
        # Get total count
        total_stmt = select(func.count(MatchLog.id))
        total_result = await db.execute(total_stmt)
        total_matches = total_result.scalar() or 0
        
        if total_matches == 0:
            return AnalyticsResponse(
                total_matches=0,
                average_match_score=0.0,
                acceptance_rate=0.0,
                completed_matches=0,
                disputed_matches=0,
            )
        
        # Get average score
        avg_score_stmt = select(func.avg(MatchLog.final_score))
        avg_score_result = await db.execute(avg_score_stmt)
        average_score = float(avg_score_result.scalar() or 0.0)
        
        # Get acceptance rate
        accepted_stmt = select(func.count(MatchLog.id)).where(MatchLog.accepted == True)
        accepted_result = await db.execute(accepted_stmt)
        accepted_count = accepted_result.scalar() or 0
        acceptance_rate = accepted_count / total_matches if total_matches > 0 else 0.0
        
        # Get completed matches
        completed_stmt = select(func.count(MatchLog.id)).where(MatchLog.completed == True)
        completed_result = await db.execute(completed_stmt)
        completed_count = completed_result.scalar() or 0
        
        # Get disputed matches
        disputed_stmt = select(func.count(MatchLog.id)).where(MatchLog.dispute_occurred == True)
        disputed_result = await db.execute(disputed_stmt)
        disputed_count = disputed_result.scalar() or 0
        
        return AnalyticsResponse(
            total_matches=total_matches,
            average_match_score=average_score,
            acceptance_rate=min(1.0, acceptance_rate),
            completed_matches=completed_count,
            disputed_matches=disputed_count,
        )
    except Exception as e:
        logger.error(f"Failed to retrieve analytics: {e}", exc_info=True)
        return AnalyticsResponse(
            total_matches=0,
            average_match_score=0.0,
            acceptance_rate=0.0,
            completed_matches=0,
            disputed_matches=0,
        )
