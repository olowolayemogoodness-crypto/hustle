from typing import Any, Dict

from app.core.logging import get_logger

logger = get_logger(__name__)


def calculate_risk_penalty(features: Dict[str, Any]) -> float:
    disputes = features.get("disputes", 0.0)
    completion_rate = features.get("completion_rate", 0.0)
    availability = features.get("availability", 0.0)
    trust_score = features.get("trust_score", 0.0)
    profile_completeness = features.get("profile_completeness", 0.0)

    penalty = 0.0
    if disputes >= 3:
        penalty += min((disputes - 2) * 0.05, 0.2)
    if completion_rate < 0.7:
        penalty += min((0.7 - completion_rate) * 0.45 + 0.05, 0.25)
    if availability < 0.25:
        penalty += 0.08
    if not features.get("is_verified", False):
        penalty += 0.05
    if profile_completeness < 0.45:
        penalty += 0.08
    if trust_score < 0.3:
        penalty += 0.12

    penalty = min(penalty, 0.4)
    logger.debug("Calculated risk penalty=%s for features=%s", penalty, features)
    return penalty
