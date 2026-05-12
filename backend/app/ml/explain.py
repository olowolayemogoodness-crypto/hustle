from typing import Any, Dict, List

from app.core.logging import get_logger

logger = get_logger(__name__)


def generate_explanation(worker: Dict[str, Any], trust_score: float) -> List[str]:
    reasons: List[str] = []
    try:
        if isinstance(trust_score, (int, float)) and trust_score > 0.75:
            reasons.append("High trust score")

        distance_km = worker.get("distance_km")
        if isinstance(distance_km, (int, float)) and distance_km < 5:
            reasons.append("Very close to job")

        skill_overlap = worker.get("skill_overlap")
        if isinstance(skill_overlap, (int, float)) and skill_overlap > 0.7:
            reasons.append("Strong skill match")

        completion_rate = worker.get("completion_rate")
        if isinstance(completion_rate, (int, float)) and completion_rate > 0.85:
            reasons.append("Excellent completion history")
    except Exception as exc:
        logger.exception("Explanation generation failed: %s", exc)

    if not reasons:
        reasons.append("Standard matching criteria applied")
    return reasons[:3]
