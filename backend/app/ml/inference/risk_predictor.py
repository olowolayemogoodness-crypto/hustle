from __future__ import annotations

import logging
from pathlib import Path
from typing import Any, Tuple

import joblib
import numpy as np

from app.core.config import settings
from app.ml.features.feature_engineering import extract_log_features
from app.ml.calibration import PlattScaler
from app.ml.inference.output_contract import MLPredictionOutput

logger = logging.getLogger(__name__)


class RiskPredictor:
    """Predicts the probability that a job match will result in completion failure."""

    def __init__(self, model_path: Path | None = None, calibration_path: Path | None = None):
        self.model = None
        self.calibrator = PlattScaler()
        self.model_path = model_path or self._get_default_model_path()
        self.calibration_path = calibration_path or self._get_default_calibration_path()
        self._load_model()
        self._load_calibrator()

    def _get_default_model_path(self) -> Path:
        return Path(settings.ml_models_dir) / "risk_model.joblib"

    def _get_default_calibration_path(self) -> Path:
        return Path(settings.ml_models_dir) / "risk_calibration.joblib"

    def _load_model(self) -> None:
        """Load the trained model from disk."""
        try:
            self.model = joblib.load(self.model_path)
            logger.info(f"Loaded risk model from {self.model_path}")
        except FileNotFoundError:
            logger.warning(f"Risk model not found at {self.model_path}, using fallback")
            self.model = None
        except Exception as e:
            logger.error(f"Failed to load risk model: {e}")
            self.model = None

    def _load_calibrator(self) -> None:
        """Load calibration scaler if available."""
        self.calibrator.load(self.calibration_path)

    def predict_risk(self, features: np.ndarray) -> Tuple[MLPredictionOutput, dict]:
        """
        Predict completion risk for a match.
        features: numpy array of shape (n_features,)
        
        Returns:
            (MLPredictionOutput with calibrated probability, risk_factors dict)
            is_fallback=True indicates model was not available
        """
        if self.model is None:
            return (
                MLPredictionOutput(
                    raw_probability=0.0,
                    calibrated_probability=0.0,
                    confidence=0.0,
                    is_fallback=True,
                ),
                {},
            )

        try:
            features = np.asarray(features, dtype=float)
            features_reshaped = features.reshape(1, -1)  # Single sample
            
            # Raw prediction
            raw_probability = self.model.predict_proba(features_reshaped)[0, 1]
            
            # Calibration
            calibrated_probability = self.calibrator.calibrate(
                np.array([raw_probability])
            )[0]
            
            # Risk factors
            risk_factors = self._extract_risk_factors(features)
            
            logger.debug(
                f"Risk: raw={raw_probability:.4f}, calibrated={calibrated_probability:.4f}"
            )
            
            return (
                MLPredictionOutput(
                    raw_probability=float(raw_probability),
                    calibrated_probability=float(calibrated_probability),
                    confidence=0.8,
                    is_fallback=False,
                ),
                risk_factors,
            )
        except Exception as e:
            logger.error(f"Risk prediction failed: {e}")
            return (
                MLPredictionOutput(
                    raw_probability=0.0,
                    calibrated_probability=0.0,
                    confidence=0.0,
                    is_fallback=True,
                ),
                {},
            )

    def _extract_risk_factors(self, features: np.ndarray) -> dict:
        """Extract simple risk factors for explainability."""
        factors = {}

        # Distance risk
        distance = features[0]
        if distance > 20:
            factors["distance"] = f"High distance: {distance}km"

        # Rating risk
        rating = features[2]
        if rating < 4.0:
            factors["rating"] = f"Low rating: {rating}"

        # Completion rate risk
        completion_rate = features[3]
        if completion_rate < 0.8:
            factors["completion_rate"] = f"Low completion rate: {completion_rate}"

        # Budget risk (high budget might be riskier)
        budget = features[6]
        if budget > 1000:  # arbitrary threshold
            factors["budget"] = f"High budget: ${budget}"

        return factors