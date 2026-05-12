import os
from typing import Any, Dict, Optional

import joblib
import numpy as np
import pandas as pd
from app.config import settings
from app.core.exceptions import MLModelError, ValidationError
from app.core.logging import get_logger
from app.utils.validation import prepare_model_features

logger = get_logger(__name__)
_model: Optional[Any] = None
_model_ready = False


def load_model() -> None:
    global _model, _model_ready
    if _model is not None and _model_ready:
        return

    model_path = settings.model_path
    try:
        if not os.path.exists(model_path):
            raise FileNotFoundError(f"Model file missing at {model_path}")

        _model = joblib.load(model_path)
        if not hasattr(_model, "predict_proba"):
            raise MLModelError("Loaded artifact does not support probability prediction")

        _model_ready = True
        logger.info("Loaded ML model from %s", model_path)
    except Exception as exc:
        _model = None
        _model_ready = False
        logger.exception("Model loading failed: %s", exc)


def check_model_ready() -> bool:
    return _model_ready


def predict_success(features: Dict[str, Any]) -> float:
    try:
        sanitized = prepare_model_features(features)
        if not _model_ready:
            logger.warning("Model unavailable; using fallback probability")
            return float(settings.fallback_probability)

        X = pd.DataFrame([sanitized], columns=settings.feature_columns)
        assert _model is not None
        proba = _model.predict_proba(X)[0][1]
        probability = float(np.clip(proba, 0.0, 1.0))
        logger.debug("Predicted probability=%s for features=%s", probability, sanitized)
        return probability
    except ValidationError as exc:
        logger.warning("Prediction validation failed: %s", exc)
        return float(settings.fallback_probability)
    except Exception as exc:
        logger.exception("Prediction failed: %s", exc)
        return float(settings.fallback_probability)


load_model()

