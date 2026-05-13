from fastapi import APIRouter, Depends
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import settings
from app.core.logging import get_logger
from app.db.deps import get_db
from app.db.models.match_log import MatchLog

logger = get_logger(__name__)
router = APIRouter(prefix=f"{settings.api_prefix}/analytics", tags=["analytics"])


@router.get("/matches")
async def get_match_analytics(db: AsyncSession = Depends(get_db)):
    # Get basic stats from match logs
    stmt = select(
        func.count(MatchLog.id).label("total_matches"),
        func.avg(MatchLog.final_score).label("avg_score"),
        func.count(MatchLog.accepted).filter(MatchLog.accepted == True).label("accepted_count"),
        func.count(MatchLog.completed).filter(MatchLog.completed == True).label("completed_count"),
    )

    result = await db.execute(stmt)
    row = result.first()

    total_matches = row.total_matches or 0
    accepted_count = row.accepted_count or 0
    completed_count = row.completed_count or 0

    acceptance_rate = accepted_count / total_matches if total_matches > 0 else 0.0
    completion_rate = completed_count / accepted_count if accepted_count > 0 else 0.0

    return {
        "total_matches": total_matches,
        "average_match_score": round(row.avg_score or 0.0, 4),
        "acceptance_rate": round(acceptance_rate, 4),
        "completion_rate": round(completion_rate, 4),
        "top_performing_workers": [],  # Would need more complex query
    }