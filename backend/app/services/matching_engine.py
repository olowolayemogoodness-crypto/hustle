"""
Pure matching engine — computes scores without side effects.
No DB, no logging, no state mutations.
"""
from typing import Any, Dict, List

from app.config import settings
from app.ml.confidence import calculate_confidence
from app.ml.explain import generate_explanation
from app.ml.feature_engineering import extract_worker_features
from app.ml.model import predict_success
from app.ml.risk import calculate_risk_penalty
from app.ml.scoring import calculate_rule_score, calculate_trust_score
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


def _build_ml_payload(features: Dict[str, Any]) -> Dict[str, Any]:
    """Extract ML features for model inference."""
    return {col: features.get(col, 0.0) for col in settings.feature_columns}


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
        worker_data = worker.model_dump()
        features = extract_worker_features(job, worker_data)

        # Compute all scoring dimensions
        trust_score = calculate_trust_score(features)
        features["trust_score"] = trust_score

        ml_payload = _build_ml_payload(features)
        ml_probability = predict_success(ml_payload)

        rule_score = calculate_rule_score(features)
        risk_penalty = calculate_risk_penalty(features)

        final_score = max(
            0.0,
            settings.rule_weight * rule_score
            + settings.ml_weight * ml_probability
            - risk_penalty,
        )

        # Apply threshold filtering
        if final_score < settings.match_threshold:
            continue

        confidence = calculate_confidence(features)
        explanation_dict = generate_explanation(features, risk_penalty, confidence)
        explanation = MatchExplanation(**explanation_dict)

        # Build structured score object
        score = WorkerScore(
            worker_id=worker_data.get("id", 0),
            final_score=final_score,
            rule_score=rule_score,
            ml_probability=ml_probability,
            risk_penalty=risk_penalty,
            confidence=confidence,
            trust_score=trust_score,
            profile_completeness=features.get("profile_completeness", 0.0),
            explanation=explanation,
            metadata={
                "skill_overlap": features.get("skill_overlap", 0.0),
                "distance_score": features.get("distance_score", 0.0),
                "availability_weighted": features.get("availability_weighted", 0.0),
                "recent_activity_score": features.get("recent_activity_score", 0.0),
            },
        )
        results.append(score)

    # Rank by final_score, then by confidence, then by trust_score for determinism
    ranked = sorted(
        results,
        key=lambda s: (s.final_score, s.confidence, s.trust_score),
        reverse=True,
    )

    return ranked
