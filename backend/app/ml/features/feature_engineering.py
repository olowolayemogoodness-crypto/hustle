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


def build_feature_dataframe(match_logs: Iterable[Any]) -> pd.DataFrame:
    """Convert a sequence of MatchLog-like objects into a pandas DataFrame."""
    rows = [dict(zip(FEATURE_COLUMNS, extract_log_features(log))) for log in match_logs]
    return pd.DataFrame(rows, columns=FEATURE_COLUMNS)
