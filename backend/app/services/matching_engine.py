"""
Pure matching engine — computes scores without side effects.
No DB, no logging, no state mutations.
Includes safety layer for ML predictions and score normalization.
Provides full ranking trace for observability and debugging.
"""
from typing import List, Optional
import logging

import numpy as np

from app.core.config import settings
from app.schemas.job import JobBase
from app.schemas.match import WorkerScore, MatchExplanation
from app.schemas.worker import WorkerResponse
from app.ml.inference.acceptance_predictor import AcceptancePredictor
from app.ml.inference.risk_predictor import RiskPredictor
from app.ml.inference.ranking_trace import RankingTrace
from app.ml.inference.ranking_logger import get_ranking_logger
from app.ml.features.feature_engineering import extract_match_features

logger = logging.getLogger(__name__)


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


def _safe_clamp(value: float, min_val: float = 0.0, max_val: float = 1.0) -> float:
    """Safely clamp value and handle NaN."""
    try:
        value = float(value)
        if not np.isfinite(value):
            return (min_val + max_val) / 2.0  # Return midpoint if NaN/inf
        return max(min_val, min(max_val, value))
    except (TypeError, ValueError):
        return (min_val + max_val) / 2.0


def _calculate_final_score(
    rule_score: float,
    ml_probability: float,
    risk_probability: float,
) -> float:
    """
    Calculate final blended score with safety checks.
    
    Formula (normalized to 0-1):
        rule_score_normalized = rule_score / 100
        final_score = 0.7 * rule_score_normalized + 0.3 * ml_probability - risk_penalty
        where risk_penalty = risk_probability * 0.15
    
    Returns:
        Score in [0, 1] range
    """
    # Safety clamps
    rule_score = _safe_clamp(rule_score, 0.0, 100.0)
    ml_probability = _safe_clamp(ml_probability, 0.0, 1.0)
    risk_probability = _safe_clamp(risk_probability, 0.0, 1.0)
    
    # Normalize rule_score to 0-1 range
    rule_score_normalized = rule_score / 100.0
    
    # Blended formula (all values now in 0-1 range)
    risk_penalty = risk_probability * 0.15  # Max 0.15 penalty
    final_score = (0.7 * rule_score_normalized) + (0.3 * ml_probability) - risk_penalty
    
    # Clamp to [0, 1]
    final_score = max(0.0, min(1.0, final_score))
    
    return final_score


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

    # Experience bonus (use completed_jobs as proxy for experience)
    if worker.completed_jobs and worker.completed_jobs >= 2:
        score += min(worker.completed_jobs * 2, 20)

    # Rating bonus
    if worker.rating and worker.rating >= 4.0:
        score += (worker.rating - 4.0) * 10

    return min(score, 100.0)  # Cap at 100


def rank_candidates(job: JobBase, workers: List[WorkerResponse]) -> List[WorkerScore]:
    """
    Pure ranking function: no side effects, no DB, no logging.
    Returns structured WorkerScore objects sorted by final_score descending.
    
    Includes calibrated ML predictions and safety layer for score blending.
    Captures full ranking traces for observability in metadata.
    """
    if not workers:
        return []

    ordered_workers = preprocess_workers(workers)
    results: List[WorkerScore] = []

    # Initialize predictors
    acceptance_predictor = AcceptancePredictor()
    risk_predictor = RiskPredictor()

    # Initialize ranking logger for observability
    ranking_logger = get_ranking_logger(enable_debug=settings.enable_match_debug)

    for worker in ordered_workers:
        rule_score = calculate_simple_score(job, worker)

        # Extract features for ML
        features = extract_match_features(job, worker, rule_score)

        # Predict acceptance probability (with calibration)
        acceptance_output = acceptance_predictor.predict_probability(features)
        ml_probability = acceptance_output.calibrated_probability
        ml_fallback = getattr(acceptance_output, 'is_fallback', False)

        # Predict completion risk (with calibration)
        risk_output, risk_factors = risk_predictor.predict_risk(features)
        risk_probability = risk_output.calibrated_probability
        risk_fallback = getattr(risk_output, 'is_fallback', False)

        # Calculate final blended score with safety layer
        risk_penalty = risk_probability * 0.15  # Normalized to 0-1 scale
        final_score = _calculate_final_score(rule_score, ml_probability, risk_probability)

        # Create ranking trace for observability
        trace = None
        try:
            trace = RankingTrace(
                worker_id=str(worker.id),
                job_id=str(job.id),
                rule_score=rule_score,
                ml_acceptance_raw=acceptance_output.raw_probability,
                ml_acceptance_calibrated=ml_probability,
                risk_probability_raw=risk_output.raw_probability,
                risk_probability_calibrated=risk_probability,
                risk_penalty=risk_penalty,
                final_score=final_score,
                ml_acceptance_fallback=ml_fallback,
                risk_model_fallback=risk_fallback,
            )
            ranking_logger.log_ranking_decision(trace, final_score >= settings.match_threshold)
        except Exception as e:
            ranking_logger.log_trace_error(str(job.id), str(worker.id), str(e))

        # Log score breakdown for observability
        logger.debug(
            f"Worker {worker.id}: rule={rule_score:.1f}, "
            f"ml_raw={acceptance_output.raw_probability:.3f}, "
            f"ml_cal={ml_probability:.3f}, "
            f"risk_raw={risk_output.raw_probability:.3f}, "
            f"risk_cal={risk_probability:.3f}, "
            f"penalty={risk_penalty:.2f}, "
            f"final={final_score:.1f}"
        )

        # Apply threshold filtering (convert match_threshold from 0-100 to 0-1 scale)
        normalized_threshold = settings.match_threshold / 100.0
        if final_score < normalized_threshold:
            continue

        # Create explanation
        explanation = MatchExplanation(
            primary_reason="Blended rule-based and calibrated ML scoring with risk adjustment",
            factors=[
                f"Distance: {worker.distance_km or 'unknown'} km",
                f"Skill overlap: {len(set(job.required_skills or []) & set(worker.skills or []))} skills",
                f"Experience: {worker.completed_jobs or 0} jobs completed",
                f"Rating: {worker.rating or 0:.1f}",
                f"ML acceptance (calibrated): {ml_probability:.3f}",
                f"Risk probability (calibrated): {risk_probability:.3f}",
                f"Final score: {final_score:.1f}",
            ]
        )

        # Build structured score object
        metadata = {
            "skill_overlap": len(set(job.required_skills or []) & set(worker.skills or [])),
            "distance_km": worker.distance_km,
            "completed_jobs": worker.completed_jobs or 0,
            "rating": worker.rating or 0.0,
            "completion_risk_probability": risk_probability,
            "risk_factors": risk_factors,
            "raw_acceptance_probability": acceptance_output.raw_probability,
            "raw_risk_probability": risk_output.raw_probability,
        }

        # Add trace to metadata if available
        if trace and settings.enable_ranking_trace:
            metadata["ranking_trace"] = trace.to_dict()

        score = WorkerScore(
            worker_id=worker.id,
            final_score=final_score,
            rule_score=rule_score / 100.0,  # Normalize to 0-1
            ml_probability=ml_probability,
            risk_penalty=risk_penalty,
            confidence=0.8,
            trust_score=(worker.rating or 5.0) / 5.0,  # Normalize rating (5.0 scale) to 0-1 for trust_score
            profile_completeness=0.8,
            explanation=explanation,
            metadata=metadata,
        )
        results.append(score)

    # Rank by final_score descending
    ranked = sorted(
        results,
        key=lambda s: s.final_score,
        reverse=True,
    )

    # Log matching summary
    if settings.enable_match_debug:
        ranking_logger.log_matching_summary(
            str(job.id),
            len(ordered_workers),
            len(ranked),
        )

    return ranked
