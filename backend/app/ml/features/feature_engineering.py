from __future__ import annotations

from typing import Any, Iterable

import numpy as np
import pandas as pd

FEATURE_COLUMNS = [
    "distance_km",
    "skill_overlap_ratio",
    "worker_rating",
    "worker_completion_rate",
    "worker_trust_score",
    "years_experience",
    "job_budget",
    "job_urgency",
    "rule_score",
]


def _safe_float(value: Any, default: float = 0.0) -> float:
    if value is None:
        return default
    if isinstance(value, bool):
        return float(value)
    try:
        return float(value)
    except (TypeError, ValueError):
        return default


def extract_log_features(match_log: Any) -> np.ndarray:
    """Extract a numeric feature vector from a MatchLog-like object."""
    values = [
        _safe_float(getattr(match_log, "distance_km", None)),
        _safe_float(getattr(match_log, "skill_overlap_ratio", None)),
        _safe_float(getattr(match_log, "worker_rating", None)),
        _safe_float(getattr(match_log, "worker_completion_rate", None)),
        _safe_float(getattr(match_log, "worker_trust_score", None)),
        _safe_float(getattr(match_log, "years_experience", None)),
        _safe_float(getattr(match_log, "job_budget", None)),
        _safe_float(getattr(match_log, "job_urgency", None)),
        _safe_float(getattr(match_log, "rule_score", None)),
    ]
    return np.asarray(values, dtype=float)


def extract_match_features(job: Any, worker: Any, rule_score: float) -> np.ndarray:
    """Extract features for ML prediction from job, worker, and rule_score."""
    values = [
        _safe_float(getattr(worker, "distance_km", None)),
        _safe_float(getattr(worker, "skill_overlap", None)),
        _safe_float(getattr(worker, "rating", None)),
        _safe_float(getattr(worker, "completion_rate", None)),
        _safe_float(getattr(worker, "trust_score", None)),
        _safe_float(getattr(worker, "completed_jobs", None)),
        _safe_float(getattr(job, "budget", None)),
        _safe_float(getattr(job, "urgency", None)),
        rule_score,
    ]
    return np.asarray(values, dtype=float)


def features_from_dict(data: dict) -> np.ndarray:
    """
    Extract features for ML prediction from a dictionary.
    
    Expected keys: distance_km, skill_overlap, rating, completion_rate,
                   disputes (optional), availability (optional)
    """
    values = [
        _safe_float(data.get("distance_km", None)),
        _safe_float(data.get("skill_overlap", None)),
        _safe_float(data.get("rating", None)),
        _safe_float(data.get("completion_rate", None)),
        _safe_float(data.get("trust_score", None)),
        _safe_float(data.get("completed_jobs", None)),
        _safe_float(data.get("job_budget", None)),
        _safe_float(data.get("job_urgency", None)),
        _safe_float(data.get("rule_score", 0.5)),  # Default to 0.5 if not provided
    ]
    return np.asarray(values, dtype=float)


def build_feature_dataframe(match_logs: list[object]) -> pd.DataFrame:
    """Build a pandas DataFrame from a list of match log objects."""
    rows = [extract_log_features(log) for log in match_logs]
    return pd.DataFrame(rows, columns=FEATURE_COLUMNS)
