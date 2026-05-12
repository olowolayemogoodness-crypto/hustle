from fastapi import APIRouter
from app.config import settings
from app.core.logging import get_logger
from app.ml.model import predict_success
from app.schemas.prediction import PredictionInput, PredictionResponse

logger = get_logger(__name__)
router = APIRouter(prefix=settings.api_prefix, tags=["prediction"])

@router.post("/predict", response_model=PredictionResponse)
def predict(input_data: PredictionInput):
    logger.info("Received /predict request")
    features = input_data.model_dump(exclude_none=True)
    probability = predict_success(features)
    logger.info("Completed prediction with probability=%.4f", probability)
    return {"success_probability": probability}
