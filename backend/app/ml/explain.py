from typing import Any, Dict, List

from app.core.logging import get_logger

logger = get_logger(__name__)


def generate_explanation(features: Dict[str, Any], risk_penalty: float, confidence: float) -> Dict[str, List[str]]:
    strengths: List[str] = []
    warnings: List[str] = []

    try:
        if features.get("skill_overlap", 0.0) >= 0.75:
            strengths.append("Excellent skill overlap")
        elif features.get("skill_overlap", 0.0) >= 0.5:
            strengths.append("Strong skill match")

        if features.get("trust_score", 0.0) >= 0.75:
            strengths.append("High trust score")

        if features.get("profile_completeness", 0.0) >= 0.75:
            strengths.append("Well-rounded profile")

        if features.get("availability_weighted", 0.0) >= 0.9:
            strengths.append("Highly available right now")

        if features.get("distance_score", 0.0) >= 0.8:
            strengths.append("Close to job location")

        if features.get("recent_activity_score", 0.0) >= 0.75:
            strengths.append("Recently active on the platform")

        if risk_penalty >= 0.15:
            warnings.append("Risk penalty applied for dispute or profile concerns")
        elif risk_penalty >= 0.05:
            warnings.append("Minor penalty from trust or activity signals")

        if confidence >= 0.8:
            strengths.append("High confidence match")
        elif confidence < 0.5:
            warnings.append("Moderate confidence; consider reviewing alternatives")

    except Exception as exc:
        logger.exception("Explanation generation failed: %s", exc)

    if not strengths:
        strengths.append("Relevant match for this job")
    if not warnings:
        warnings.append("No major concerns detected")

    return {
        "strengths": strengths[:3],
        "warnings": warnings[:3],
    }
