from typing import Any, Dict, List

from app.config import settings
from app.core.logging import get_logger

logger = get_logger(__name__)


def _safe_float(value: Any, default: float = 0.0, scale: float | None = 1.0) -> float:
    try:
        if value is None:
            return default
        if isinstance(value, bool):
            return default
        value_float = float(value)
        if value_float != value_float:
            return default
        if scale is not None:
            return max(0.0, min(value_float, scale))
        return max(0.0, value_float)
    except (TypeError, ValueError):
        return default


def _normalize(value: Any, default: float = 0.0, scale: float = 1.0) -> float:
    if scale <= 0:
        return default
    return _safe_float(value, default=default, scale=scale) / scale


def compute_skill_overlap(required_skills: List[str], worker_skills: List[str]) -> float:
    if not required_skills or not worker_skills:
        return 0.0
    overlap = len(set(required_skills).intersection(set(worker_skills)))
    return min(overlap / max(len(required_skills), 1), 1.0)


def compute_profile_completeness(worker: Dict[str, Any]) -> float:
    score = 0.0
    score += 0.18 if worker.get("bio") else 0.0
    score += 0.22 if worker.get("skills") else 0.0
    score += 0.18 if worker.get("verified") else 0.0
    score += 0.14 if worker.get("rating") is not None else 0.0
    score += 0.14 if worker.get("availability") is not None else 0.0
    score += 0.14 if worker.get("latitude") is not None and worker.get("longitude") is not None else 0.0
    return min(score, 1.0)


def compute_recent_activity_score(worker: Dict[str, Any]) -> float:
    days = worker.get("recent_activity_days")
    availability = _normalize(worker.get("availability"), default=0.0, scale=1.0)
    completion_rate = _normalize(worker.get("completion_rate"), default=0.0, scale=1.0)
    if isinstance(days, (int, float)) and days >= 0:
        recent = max(0.0, min(1.0, 1.0 - min(days, 30) / 30.0))
        return 0.7 * recent + 0.3 * availability
    return min(1.0, 0.3 + 0.5 * availability + 0.2 * completion_rate)


def extract_worker_features(job: Any, worker: Dict[str, Any]) -> Dict[str, Any]:
    skills = worker.get("skills", []) or []
    skill_overlap = _safe_float(worker.get("skill_overlap"), default=None, scale=1.0)
    if skill_overlap is None or skill_overlap <= 0.0:
        skill_overlap = compute_skill_overlap(job.required_skills, skills)

    availability = _normalize(worker.get("availability"), default=0.0, scale=1.0)
    availability_weighted = min(1.0, availability * 1.2)

    distance_km = _safe_float(worker.get("distance_km"), default=settings.max_worker_search_radius)
    distance_score = max(0.0, 1.0 - min(distance_km, settings.max_worker_search_radius) / settings.max_worker_search_radius)

    completion_rate = worker.get("completion_rate")
    if completion_rate is None:
        completion_rate = settings.fallback_probability
    completion_rate = _normalize(completion_rate, default=0.0, scale=1.0)

    rating = _safe_float(worker.get("rating"), default=settings.fallback_probability * 5, scale=5.0)
    disputes = _safe_float(worker.get("disputes"), default=0.0, scale=10.0)
    is_verified = bool(worker.get("verified"))
    skills_count = len(skills)
    experience_level = worker.get("experience_level", "entry")
    experience_bonus = 0.1 if experience_level in {"mid", "senior", "expert"} else 0.0

    profile_completeness = compute_profile_completeness(worker)
    recent_activity_score = compute_recent_activity_score(worker)

    extracted = {
        "distance_km": distance_km,
        "distance_score": distance_score,
        "skill_overlap": skill_overlap,
        "availability": availability,
        "availability_weighted": availability_weighted,
        "completion_rate": completion_rate,
        "rating": rating,
        "disputes": disputes,
        "is_verified": is_verified,
        "skills_count": skills_count,
        "experience_bonus": experience_bonus,
        "profile_completeness": profile_completeness,
        "recent_activity_score": recent_activity_score,
        "experience_level": experience_level,
    }

    logger.debug("Extracted worker features: %s", extracted)
    return extracted
