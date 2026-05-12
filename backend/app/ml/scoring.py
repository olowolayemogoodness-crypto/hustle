from typing import Any, Dict


def _safe_normalize(value: Any, default: float = 0.0, scale: float = 1.0) -> float:
    try:
        if value is None:
            return default
        result = float(value)
        if result != result:
            return default
        return max(0.0, min(result, scale))
    except (TypeError, ValueError):
        return default


def calculate_trust_score(worker: Dict[str, Any]) -> float:
    completion_rate = _safe_normalize(worker.get("completion_rate"), default=0.0, scale=1.0)
    rating = _safe_normalize(worker.get("rating"), default=0.0, scale=5.0) / 5.0
    disputes = _safe_normalize(worker.get("disputes"), default=0.0, scale=10.0)
    availability = _safe_normalize(worker.get("availability"), default=0.0, scale=1.0)

    score = (
        0.4 * completion_rate
        + 0.3 * rating
        + 0.2 * (1.0 - min(disputes / 10.0, 1.0))
        + 0.1 * availability
    )
    return round(score, 4)


def calculate_matching_score(
    distance_km: Any,
    skill_overlap: Any,
    trust_score: Any,
    availability: Any,
) -> float:
    distance = _safe_normalize(distance_km, default=20.0)
    distance_score = max(0.0, 1.0 - min(distance, 20.0) / 20.0)
    skill_overlap_score = _safe_normalize(skill_overlap, default=0.0, scale=1.0)
    trust = _safe_normalize(trust_score, default=0.0, scale=1.0)
    available = _safe_normalize(availability, default=0.0, scale=1.0)

    score = (
        0.3 * distance_score
        + 0.3 * skill_overlap_score
        + 0.3 * trust
        + 0.1 * available
    )
    return round(score, 4)
