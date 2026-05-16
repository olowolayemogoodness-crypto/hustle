"""
Unified ML inference output contract.
Both acceptance and risk models return this structure.
"""
from __future__ import annotations

from dataclasses import dataclass


@dataclass
class MLPredictionOutput:
    """
    Unified ML prediction output with calibration.
    
    Attributes:
        raw_probability: Raw model output [0, 1]
        calibrated_probability: Platt-scaled probability [0, 1]
        confidence: Model confidence level [0, 1]
        is_fallback: Whether this used fallback (no model/calibration available)
    """
    raw_probability: float
    calibrated_probability: float
    confidence: float = 0.5
    is_fallback: bool = False

    def __post_init__(self) -> None:
        """Clamp all values to [0, 1]."""
        self.raw_probability = max(0.0, min(1.0, self.raw_probability))
        self.calibrated_probability = max(0.0, min(1.0, self.calibrated_probability))
        self.confidence = max(0.0, min(1.0, self.confidence))

    def to_dict(self) -> dict:
        """Return as dict for serialization."""
        return {
            "raw_probability": self.raw_probability,
            "calibrated_probability": self.calibrated_probability,
            "confidence": self.confidence,
            "is_fallback": self.is_fallback,
        }
