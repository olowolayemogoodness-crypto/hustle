from __future__ import annotations

import logging
from pathlib import Path
from typing import Any

import joblib
import numpy as np

from app.core.config import settings
from app.ml.features.feature_engineering import extract_log_features
from app.ml.calibration import PlattScaler
from app.ml.inference.output_contract import MLPredictionOutput

logger = logging.getLogger(__name__)


class AcceptancePredictor:
    """Predicts the probability that a worker will accept a job match."""

    def __init__(self, model_path: Path | None = None, calibration_path: Path | None = None):
        self.model = None
        self.calibrator = PlattScaler()
        self.model_path = model_path or self._get_default_model_path()
        self.calibration_path = calibration_path or self._get_default_calibration_path()
        self._load_model()
        self._load_calibrator()

    def _get_default_model_path(self) -> Path:
        return Path(settings.ml_models_dir) / "acceptance_model.joblib"

    def _get_default_calibration_path(self) -> Path:
        return Path(settings.ml_models_dir) / "acceptance_calibration.joblib"

    def _load_model(self) -> None:
        """Load the trained model from disk."""
        try:
            self.model = joblib.load(self.model_path)
            logger.info(f"Loaded acceptance model from {self.model_path}")
        except FileNotFoundError:
            logger.warning(f"Acceptance model not found at {self.model_path}, using fallback")
            self.model = None
        except Exception as e:
            logger.error(f"Failed to load acceptance model: {e}")
            self.model = None

    def _load_calibrator(self) -> None:
        """Load calibration scaler if available."""
        self.calibrator.load(self.calibration_path)

    def predict_probability(self, features: np.ndarray) -> MLPredictionOutput:
        """
        Predict acceptance probability for a match.
        features: numpy array of shape (n_features,)
        
        Returns:
            MLPredictionOutput with raw and calibrated probabilities
            is_fallback=True indicates model was not available
        """
        if self.model is None:
            # Fallback: neutral probability
            return MLPredictionOutput(
                raw_probability=0.5,
                calibrated_probability=0.5,
                confidence=0.0,
                is_fallback=True,
            )

        try:
            features = np.asarray(features, dtype=float)
            features = features.reshape(1, -1)  # Single sample
            
            # Raw prediction
            raw_probability = self.model.predict_proba(features)[0, 1]
            
            # Calibration
            calibrated_probability = self.calibrator.calibrate(
                np.array([raw_probability])
            )[0]
            
            logger.debug(
                f"Acceptance: raw={raw_probability:.4f}, calibrated={calibrated_probability:.4f}"
            )
            
            return MLPredictionOutput(
                raw_probability=float(raw_probability),
                calibrated_probability=float(calibrated_probability),
                confidence=0.8,
                is_fallback=False,
            )
        except Exception as e:
            logger.error(f"Prediction failed: {e}")
            return MLPredictionOutput(
                raw_probability=0.5,
                calibrated_probability=0.5,
                confidence=0.0,
                is_fallback=True,
            )