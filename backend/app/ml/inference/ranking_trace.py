"""
Ranking trace data structure for full observability.
Captures all components of the scoring decision for debugging and monitoring.
"""
from __future__ import annotations

from dataclasses import dataclass, asdict
from typing import Optional


@dataclass
class RankingTrace:
    """
    Complete trace of a single worker's ranking decision.
    
    Captures all score components for full transparency and debugging.
    """
    worker_id: str
    job_id: str
    
    # Rule-based score
    rule_score: float
    
    # ML acceptance probability (both raw and calibrated)
    ml_acceptance_raw: float
    ml_acceptance_calibrated: float
    
    # Risk probability (both raw and calibrated)
    risk_probability_raw: float
    risk_probability_calibrated: float
    
    # Penalty calculation
    risk_penalty: float
    
    # Final blended score
    final_score: float
    
    # Fallback flags
    ml_acceptance_fallback: bool = False
    risk_model_fallback: bool = False
    
    # Optional metadata
    model_version: Optional[str] = None
    timestamp: Optional[str] = None
    
    def __post_init__(self) -> None:
        """Validate trace has no NaN or invalid values."""
        self._validate()
    
    def _validate(self) -> None:
        """Ensure all numerical fields are valid."""
        import math
        
        fields_to_check = [
            "rule_score",
            "ml_acceptance_raw",
            "ml_acceptance_calibrated",
            "risk_probability_raw",
            "risk_probability_calibrated",
            "risk_penalty",
            "final_score",
        ]
        
        for field in fields_to_check:
            value = getattr(self, field)
            if not isinstance(value, (int, float)):
                raise ValueError(f"{field} must be numeric, got {type(value)}")
            if math.isnan(value) or math.isinf(value):
                raise ValueError(f"{field} contains NaN or Inf: {value}")
    
    def to_dict(self) -> dict:
        """Convert to dict for JSON serialization."""
        return asdict(self)
    
    def to_log_dict(self) -> dict:
        """Convert to dict for structured logging (minimal)."""
        return {
            "worker_id": self.worker_id,
            "job_id": self.job_id,
            "rule_score": round(self.rule_score, 3),
            "ml_acceptance": round(self.ml_acceptance_calibrated, 3),
            "risk_penalty": round(self.risk_penalty, 3),
            "final_score": round(self.final_score, 1),
            "fallbacks": {
                "ml_acceptance": self.ml_acceptance_fallback,
                "risk_model": self.risk_model_fallback,
            },
        }
