from typing import Any, Dict, List

from app.config import settings
from app.core.logging import get_logger
from app.ml.confidence import calculate_confidence
from app.ml.explain import generate_explanation
from app.ml.feature_engineering import extract_worker_features
from app.ml.model import predict_success
from app.ml.ranking import rank_workers
from app.ml.risk import calculate_risk_penalty
from app.ml.scoring import calculate_rule_score, calculate_trust_score
from app.schemas.job import JobBase
from app.schemas.worker import WorkerResponse

logger = get_logger(__name__)


def preprocess_workers(workers: List[WorkerResponse]) -> List[WorkerResponse]:
    filtered_workers = [
        worker
        for worker in workers
        if worker.distance_km is None or worker.distance_km <= settings.max_worker_search_radius
    ]
    return sorted(
        filtered_workers,
        key=lambda worker: (worker.distance_km if worker.distance_km is not None else 999.0),
    )[: settings.max_workers_evaluated]


def _build_ml_payload(features: Dict[str, Any]) -> Dict[str, Any]:
    return {column: features.get(column, 0.0) for column in settings.feature_columns}


def match_workers(job: JobBase, workers: List[WorkerResponse]) -> List[Dict[str, Any]]:
    if not workers:
        logger.info("No workers supplied for job %s", job.id)
        return []

    ordered_workers = preprocess_workers(workers)
    results: List[Dict[str, Any]] = []

    for worker in ordered_workers:
        worker_data = worker.model_dump()
        features = extract_worker_features(job, worker_data)
        trust_score = calculate_trust_score(features)
        features["trust_score"] = trust_score

        ml_payload = _build_ml_payload(features)
        ml_probability = predict_success(ml_payload)

        rule_score = calculate_rule_score(features)
        risk_penalty = calculate_risk_penalty(features)
        final_score = round(
            max(0.0, settings.rule_weight * rule_score + settings.ml_weight * ml_probability - risk_penalty),
            4,
        )

        if final_score < settings.match_threshold:
            logger.debug(
                "Worker %s did not meet threshold %.4f",
                worker_data.get("id"),
                settings.match_threshold,
            )
            continue

        confidence = calculate_confidence(features)
        explanation = generate_explanation(features, risk_penalty, confidence)

        results.append(
            {
                "worker_id": worker_data.get("id", 0),
                "final_score": final_score,
                "rule_score": round(rule_score, 4),
                "trust_score": round(trust_score, 4),
                "ml_probability": round(ml_probability, 4),
                "risk_penalty": round(risk_penalty, 4),
                "confidence": round(confidence, 4),
                "profile_completeness": round(features.get("profile_completeness", 0.0), 4),
                "explanation": explanation,
                "metadata": {
                    "skill_overlap": round(features.get("skill_overlap", 0.0), 4),
                    "distance_score": round(features.get("distance_score", 0.0), 4),
                    "availability_weighted": round(features.get("availability_weighted", 0.0), 4),
                    "recent_activity_score": round(features.get("recent_activity_score", 0.0), 4),
                },
            }
        )

    ranked = rank_workers(results)
    logger.info("Ranked %d workers for job %s", len(ranked), job.id)
    return ranked
