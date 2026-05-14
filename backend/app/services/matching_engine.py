"""
Pure matching engine — computes scores without side effects.
No DB, no logging, no state mutations.
"""
from typing import List

from app.core.config import settings
from app.schemas.job import JobBase
from app.schemas.match import WorkerScore, MatchExplanation
from app.schemas.worker import WorkerResponse


def preprocess_workers(workers: List[WorkerResponse]) -> List[WorkerResponse]:
    """Filter workers by distance and limit."""
    filtered = [
        w for w in workers
        if w.distance_km is None or w.distance_km <= settings.max_worker_search_radius
    ]
    return sorted(
        filtered,
        key=lambda w: w.distance_km if w.distance_km else 999.0,
    )[: settings.max_workers_evaluated]


def calculate_simple_score(job: JobBase, worker: WorkerResponse) -> float:
    """Calculate a simple rule-based score for worker-job match."""
    score = 0.0

    # Distance scoring (closer is better)
    if worker.distance_km is not None:
        if worker.distance_km <= 5:
            score += 30
        elif worker.distance_km <= 10:
            score += 20
        elif worker.distance_km <= 20:
            score += 10
        elif worker.distance_km <= 50:
            score += 5

    # Skill matching (basic overlap)
    job_skills = set(job.required_skills or [])
    worker_skills = set(worker.skills or [])
    skill_overlap = len(job_skills & worker_skills)
    if job_skills:
        skill_match_ratio = skill_overlap / len(job_skills)
        score += skill_match_ratio * 40

    # Experience bonus
    if worker.years_experience and worker.years_experience >= 2:
        score += min(worker.years_experience * 2, 20)

    # Rating bonus
    if worker.average_rating and worker.average_rating >= 4.0:
        score += (worker.average_rating - 4.0) * 10

    return min(score, 100.0)  # Cap at 100


def rank_candidates(job: JobBase, workers: List[WorkerResponse]) -> List[WorkerScore]:
    """
    Pure ranking function: no side effects, no DB, no logging.
    Returns structured WorkerScore objects sorted by final_score descending.
    """
    if not workers:
        return []

    ordered_workers = preprocess_workers(workers)
    results: List[WorkerScore] = []

    for worker in ordered_workers:
        final_score = calculate_simple_score(job, worker)

        # Apply threshold filtering
        if final_score < settings.match_threshold:
            continue

        # Create simple explanation
        explanation = MatchExplanation(
            primary_reason="Distance and skill match",
            factors=[
                f"Distance: {worker.distance_km or 'unknown'} km",
                f"Skill overlap: {len(set(job.required_skills or []) & set(worker.skills or []))} skills",
                f"Experience: {worker.years_experience or 0} years",
                f"Rating: {worker.average_rating or 0:.1f}"
            ]
        )

        # Build structured score object
        score = WorkerScore(
            worker_id=worker.id,
            final_score=final_score,
            rule_score=final_score,
            ml_probability=0.0,  # Not used in MVP
            risk_penalty=0.0,    # Not used in MVP
            confidence=0.8,      # Fixed confidence for MVP
            trust_score=worker.average_rating or 0.0,
            profile_completeness=0.8,  # Fixed for MVP
            explanation=explanation,
            metadata={
                "skill_overlap": len(set(job.required_skills or []) & set(worker.skills or [])),
                "distance_km": worker.distance_km,
                "years_experience": worker.years_experience or 0,
                "average_rating": worker.average_rating or 0.0,
            },
        )
        results.append(score)

    # Rank by final_score descending
    ranked = sorted(
        results,
        key=lambda s: s.final_score,
        reverse=True,
    )

    return ranked
