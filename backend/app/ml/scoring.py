from typing import Any, Dict


def _safe_normalize(value: Any, default: float = 0.0, scale: float = 1.0) -> float:
    try:
        if value is None:
            return default
        if isinstance(value, bool):
            return default
        result = float(value)
        if result != result:
            return default
        return max(0.0, min(result, scale))
    except (TypeError, ValueError):
        return default


def calculate_trust_score(features: Dict[str, Any]) -> float:
    completion_rate = _safe_normalize(features.get("completion_rate"), default=0.0, scale=1.0)
    rating = _safe_normalize(features.get("rating"), default=0.0, scale=5.0)
    disputes = _safe_normalize(features.get("disputes"), default=0.0, scale=10.0)
    availability = _safe_normalize(features.get("availability"), default=0.0, scale=1.0)
    profile_completeness = _safe_normalize(features.get("profile_completeness"), default=0.0, scale=1.0)

    score = (
        0.35 * completion_rate
        + 0.25 * (rating / 5.0)
        + 0.2 * (1.0 - min(disputes / 10.0, 1.0))
        + 0.1 * availability
        + 0.1 * profile_completeness
    )
    return min(max(score, 0.0), 1.0)


def calculate_rule_score(features: Dict[str, Any]) -> float:
    distance_score = _safe_normalize(features.get("distance_score"), default=0.0, scale=1.0)
    skill_overlap = _safe_normalize(features.get("skill_overlap"), default=0.0, scale=1.0)
    trust_score = _safe_normalize(features.get("trust_score"), default=0.0, scale=1.0)
    availability_weighted = _safe_normalize(features.get("availability_weighted"), default=0.0, scale=1.0)
    recent_activity = _safe_normalize(features.get("recent_activity_score"), default=0.0, scale=1.0)

    score = (
        0.24 * distance_score
        + 0.28 * skill_overlap
        + 0.24 * trust_score
        + 0.12 * availability_weighted
        + 0.12 * recent_activity
    )
    return min(max(score, 0.0), 1.0)
