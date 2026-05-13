from typing import Any, Dict


def calculate_confidence(features: Dict[str, Any]) -> float:
    skill_overlap = float(features.get("skill_overlap", 0.0))
    trust_score = float(features.get("trust_score", 0.0))
    completion_rate = float(features.get("completion_rate", 0.0))
    availability_weighted = float(features.get("availability_weighted", 0.0))
    profile_completeness = float(features.get("profile_completeness", 0.0))

    confidence = (
        0.35 * skill_overlap
        + 0.25 * trust_score
        + 0.2 * completion_rate
        + 0.1 * availability_weighted
        + 0.1 * profile_completeness
    )
    return min(max(confidence, 0.0), 1.0)
