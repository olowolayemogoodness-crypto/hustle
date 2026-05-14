import math
from typing import Any, Dict
from app.core.config import settings
from app.core.exceptions import ValidationError


def is_finite_number(value: Any) -> bool:
    if isinstance(value, bool):
        return False
    if isinstance(value, (int, float)):
        return not math.isnan(value) and not math.isinf(value)
    return False


def to_float(value: Any, default: float = 0.0) -> float:
    if value is None:
        return default
    if is_finite_number(value):
        return float(value)
    if isinstance(value, str):
        try:
            return float(value)
        except ValueError:
            return default
    return default


def prepare_model_features(raw: Dict[str, Any]) -> Dict[str, float]:
    if raw is None:
        raise ValidationError("Feature payload is required.")
    if not isinstance(raw, dict):
        raise ValidationError("Feature payload must be a JSON object.")

    features: Dict[str, float] = {}
    for column in settings.feature_columns:
        features[column] = to_float(raw.get(column), default=0.0)
    return features
