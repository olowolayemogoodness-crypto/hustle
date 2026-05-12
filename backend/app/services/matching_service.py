from typing import Any, Dict, List

from app.config import settings
from app.core.logging import get_logger
from app.ml.explain import generate_explanation
from app.ml.model import predict_success
from app.ml.scoring import calculate_matching_score, calculate_trust_score
from app.schemas.job import JobBase
from app.schemas.worker import WorkerResponse

logger = get_logger(__name__)


def compute_skill_overlap(required_skills: List[str], worker_skills: List[str]) -> float:
    if not required_skills or not worker_skills:
        return 0.0
    overlap = len(set(required_skills).intersection(set(worker_skills)))
    return float(overlap) / max(len(required_skills), 1)


def match_workers(job: JobBase, workers: List[WorkerResponse]) -> List[Dict[str, Any]]:
    if not workers:
        logger.info("No workers supplied for job %s", job.id)
        return []

    ordered_workers = sorted(
        workers,
        key=lambda worker: (worker.distance_km if worker.distance_km is not None else 999.0),
    )[: settings.max_workers_evaluated]

    results: List[Dict[str, Any]] = []

    for worker in ordered_workers:
        worker_data = worker.model_dump()
        skill_overlap = worker_data.get("skill_overlap")
        if skill_overlap is None:
            skill_overlap = compute_skill_overlap(job.required_skills, worker_data.get("skills", []))

        distance_km = worker_data.get("distance_km")
        if distance_km is None:
            distance_km = 20.0

        trust_score = calculate_trust_score(worker_data)
        match_score = calculate_matching_score(
            distance_km,
            skill_overlap,
            trust_score,
            worker_data.get("availability", 0.0),
        )

        features = {
            "distance_km": distance_km,
            "skill_overlap": skill_overlap,
            "trust_score": trust_score,
            "rating": worker_data.get("rating", 0.0),
            "completion_rate": worker_data.get("completion_rate", 0.0),
            "disputes": worker_data.get("disputes", 0),
            "availability": worker_data.get("availability", 0.0),
        }

        ml_probability = predict_success(features)
        final_score = settings.rule_weight * match_score + settings.ml_weight * ml_probability
        if final_score < settings.match_threshold:
            logger.debug("Worker %s did not meet threshold %.4f", worker_data.get("id"), settings.match_threshold)
            continue

        explanation = generate_explanation(worker_data, trust_score)
        results.append(
            {
                "worker_id": worker_data.get("id", 0),
                "final_score": round(final_score, 4),
                "trust_score": round(trust_score, 4),
                "ml_probability": round(ml_probability, 4),
                "explanation": explanation,
            }
        )

    ranked = sorted(results, key=lambda item: item["final_score"], reverse=True)
    logger.info("Ranked %d workers for job %s", len(ranked), job.id)
    return ranked
