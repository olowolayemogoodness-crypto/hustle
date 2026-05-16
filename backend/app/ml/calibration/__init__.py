"""
Probability calibration using Platt Scaling.
MVP-light calibration layer for both acceptance and risk models.
"""
from __future__ import annotations

import logging
from pathlib import Path
from typing import Tuple

import joblib
import numpy as np

logger = logging.getLogger(__name__)


class PlattScaler:
    """
    Platt Scaling for probability calibration.
    
    Fits a logistic regression to map raw model probabilities
    to calibrated probabilities using held-out data.
    
    Formula: P_calibrated = 1 / (1 + exp(A * P_raw + B))
    """

    def __init__(self):
        self.A: float | None = None
        self.B: float | None = None

    def fit(self, y_proba: np.ndarray, y_true: np.ndarray) -> None:
        """
        Fit Platt Scaling parameters.
        
        Args:
            y_proba: Raw probabilities from model [0, 1]
            y_true: Ground truth labels {0, 1}
        """
        if len(y_proba) < 2:
            logger.warning("Insufficient data for Platt calibration, using fallback")
            self.A = 0.0
            self.B = 0.0
            return

        # Safe conversion
        y_proba = np.clip(y_proba, 1e-7, 1 - 1e-7)
        y_true = np.asarray(y_true, dtype=int)

        # Compute target
        N_pos = np.sum(y_true)
        N_neg = len(y_true) - N_pos

        if N_pos == 0 or N_neg == 0:
            logger.warning("Imbalanced calibration data, using fallback")
            self.A = 0.0
            self.B = 0.0
            return

        # Log odds
        log_odds = np.log(y_proba / (1 - y_proba))
        
        # Simple linear fit: find A, B that minimize cross-entropy
        # Using pseudo-inverse for numerical stability
        X = np.column_stack([log_odds, np.ones(len(log_odds))])
        try:
            params, _, _, _ = np.linalg.lstsq(X, y_true, rcond=None)
            self.A = params[0]
            self.B = params[1]
            logger.info(f"Platt scaling fitted: A={self.A:.4f}, B={self.B:.4f}")
        except Exception as e:
            logger.error(f"Platt fit failed: {e}, using fallback")
            self.A = 0.0
            self.B = 0.0

    def calibrate(self, y_proba: np.ndarray) -> np.ndarray:
        """
        Apply Platt Scaling to raw probabilities.
        
        Args:
            y_proba: Raw probabilities [0, 1]
            
        Returns:
            Calibrated probabilities [0, 1]
        """
        if self.A is None or self.B is None:
            return y_proba

        y_proba = np.clip(y_proba, 1e-7, 1 - 1e-7)
        log_odds = np.log(y_proba / (1 - y_proba))
        
        # Sigmoid transformation
        z = self.A * log_odds + self.B
        calibrated = 1.0 / (1.0 + np.exp(-z))
        
        return np.clip(calibrated, 0.0, 1.0)

    def save(self, path: Path) -> None:
        """Save scaler to disk."""
        path.parent.mkdir(parents=True, exist_ok=True)
        joblib.dump({"A": self.A, "B": self.B}, path)
        logger.info(f"Platt scaler saved to {path}")

    def load(self, path: Path) -> None:
        """Load scaler from disk."""
        try:
            params = joblib.load(path)
            self.A = params["A"]
            self.B = params["B"]
            logger.info(f"Platt scaler loaded from {path}")
        except Exception as e:
            logger.error(f"Failed to load Platt scaler: {e}")
            self.A = 0.0
            self.B = 0.0
