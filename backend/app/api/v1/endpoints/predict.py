"""Prediction endpoint for ML model inference."""
from fastapi import APIRouter
from pydantic import BaseModel, Field

from app.core.config import settings
from app.core.logging import get_logger
from app.ml.inference.acceptance_predictor import AcceptancePredictor
from app.ml.features.feature_engineering import features_from_dict

logger = get_logger(__name__)
router = APIRouter(prefix=settings.api_prefix, tags=["predict"])


class PredictRequest(BaseModel):
    """Request payload for match prediction."""
    distance_km: float = Field(..., ge=0.0, description="Distance in km")
    skill_overlap: float = Field(..., ge=0.0, le=1.0, description="Skill overlap ratio")
    rating: float = Field(..., ge=0.0, le=5.0, description="Worker rating")
    completion_rate: float = Field(..., ge=0.0, le=1.0, description="Completion rate")
    disputes: int = Field(default=0, ge=0, description="Number of disputes")
    availability: float = Field(..., ge=0.0, le=1.0, description="Availability")


class PredictResponse(BaseModel):
    """Response with prediction result."""
    success_probability: float = Field(..., ge=0.0, le=1.0, description="Predicted acceptance probability")
    raw_probability: float = Field(default=None, ge=0.0, le=1.0, description="Raw model output")
    is_fallback: bool = Field(default=False, description="Whether fallback was used")


@router.post("/predict", response_model=PredictResponse)
async def predict(payload: PredictRequest) -> PredictResponse:
    """
    Predict worker acceptance probability for a job match.
    
    Uses the acceptance prediction model with calibration.
    Falls back to base rate if model is unavailable.
    """
    logger.info("Predicting match acceptance for worker features")
    
    try:
        # Build feature array from request
        features = features_from_dict({
            "distance_km": payload.distance_km,
            "skill_overlap": payload.skill_overlap,
            "rating": payload.rating,
            "completion_rate": payload.completion_rate,
            "disputes": payload.disputes,
            "availability": payload.availability,
        })
        
        # Get prediction
        predictor = AcceptancePredictor()
        output = predictor.predict_probability(features)
        
        return PredictResponse(
            success_probability=output.calibrated_probability,
            raw_probability=output.raw_probability,
            is_fallback=getattr(output, 'is_fallback', False),
        )
    except Exception as e:
        logger.error(f"Prediction failed: {e}", exc_info=True)
        # Return fallback
        return PredictResponse(
            success_probability=settings.fallback_probability,
            raw_probability=settings.fallback_probability,
            is_fallback=True,
        )
