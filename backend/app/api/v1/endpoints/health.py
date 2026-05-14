from fastapi import APIRouter, Depends, status
from fastapi.responses import JSONResponse
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.deps import get_db

router = APIRouter(prefix="/health", tags=["health"])

@router.get("/live")
def liveness():
    return {"status": "alive"}

@router.get("/ready")
async def readiness(db: AsyncSession = Depends(get_db)):
    try:
        # Simple database connectivity check
        await db.execute("SELECT 1")
        return {"status": "ready", "database": "connected"}
    except Exception:
        return JSONResponse(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            content={"status": "degraded", "database": "disconnected"},
        )
