from fastapi import APIRouter, status
from fastapi.responses import JSONResponse
from app.ml import model as ml_model

router = APIRouter(prefix="/health", tags=["health"])

@router.get("/live")
def liveness():
    return {"status": "alive"}

@router.get("/ready")
def readiness():
    if ml_model.check_model_ready():
        return {"status": "ready", "model_ready": True}

    return JSONResponse(
        status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
        content={"status": "degraded", "model_ready": False},
    )
