"""
Tests for probability calibration and ML stability layer.
Ensures calibration, safety checks, and inference consistency.
"""
import numpy as np
import pytest
from pathlib import Path
from tempfile import TemporaryDirectory

from app.ml.calibration import PlattScaler
from app.ml.inference.acceptance_predictor import AcceptancePredictor
from app.ml.inference.risk_predictor import RiskPredictor
from app.ml.inference.output_contract import MLPredictionOutput


class TestPlattScaling:
    """Test Platt Scaling calibration."""

    def test_platt_scaler_initialization(self):
        """Test PlattScaler initializes correctly."""
        scaler = PlattScaler()
        assert scaler.A is None
        assert scaler.B is None

    def test_platt_scaler_fit(self):
        """Test PlattScaler fitting."""
        scaler = PlattScaler()
        y_proba = np.array([0.1, 0.3, 0.5, 0.7, 0.9])
        y_true = np.array([0, 0, 1, 1, 1])

        scaler.fit(y_proba, y_true)

        assert scaler.A is not None
        assert scaler.B is not None

    def test_platt_scaler_calibrate(self):
        """Test Platt Scaling calibration."""
        scaler = PlattScaler()
        y_proba = np.array([0.1, 0.3, 0.5, 0.7, 0.9])
        y_true = np.array([0, 0, 1, 1, 1])

        scaler.fit(y_proba, y_true)
        calibrated = scaler.calibrate(y_proba)

        # Output should be valid probabilities
        assert all(0.0 <= p <= 1.0 for p in calibrated)
        assert len(calibrated) == len(y_proba)

    def test_platt_scaler_fallback_on_insufficient_data(self):
        """Test fallback when insufficient data."""
        scaler = PlattScaler()
        y_proba = np.array([0.5])
        y_true = np.array([1])

        scaler.fit(y_proba, y_true)

        # Should use fallback (A=0, B=0)
        assert scaler.A == 0.0
        assert scaler.B == 0.0

    def test_platt_scaler_save_load(self):
        """Test Platt Scaler persistence."""
        with TemporaryDirectory() as tmpdir:
            scaler1 = PlattScaler()
            y_proba = np.array([0.1, 0.3, 0.5, 0.7, 0.9])
            y_true = np.array([0, 0, 1, 1, 1])
            scaler1.fit(y_proba, y_true)

            # Save
            path = Path(tmpdir) / "scaler.joblib"
            scaler1.save(path)
            assert path.exists()

            # Load
            scaler2 = PlattScaler()
            scaler2.load(path)
            assert scaler2.A == scaler1.A
            assert scaler2.B == scaler1.B


class TestMLPredictionOutput:
    """Test unified ML output contract."""

    def test_output_initialization(self):
        """Test MLPredictionOutput initialization."""
        output = MLPredictionOutput(
            raw_probability=0.75,
            calibrated_probability=0.70,
            confidence=0.9,
        )
        assert output.raw_probability == 0.75
        assert output.calibrated_probability == 0.70
        assert output.confidence == 0.9

    def test_output_clamping(self):
        """Test that probabilities are clamped to [0, 1]."""
        output = MLPredictionOutput(
            raw_probability=1.5,  # Should clamp to 1.0
            calibrated_probability=-0.1,  # Should clamp to 0.0
            confidence=2.0,  # Should clamp to 1.0
        )
        assert output.raw_probability == 1.0
        assert output.calibrated_probability == 0.0
        assert output.confidence == 1.0

    def test_output_to_dict(self):
        """Test serialization to dict."""
        output = MLPredictionOutput(
            raw_probability=0.75,
            calibrated_probability=0.70,
            confidence=0.9,
        )
        d = output.to_dict()
        assert d["raw_probability"] == 0.75
        assert d["calibrated_probability"] == 0.70
        assert d["confidence"] == 0.9


class TestAcceptancePredictorFallback:
    """Test AcceptancePredictor with missing models."""

    def test_predictor_fallback_when_model_missing(self):
        """Test fallback when model is not available."""
        predictor = AcceptancePredictor(
            model_path=Path("/nonexistent/model.joblib"),
            calibration_path=Path("/nonexistent/calibration.joblib"),
        )
        
        features = np.array([1.0, 0.5, 4.0, 0.9, 0.7, 2.0, 100.0, 2.0, 0.7])
        output = predictor.predict_probability(features)

        # Should return fallback probabilities
        assert isinstance(output, MLPredictionOutput)
        assert output.raw_probability == 0.5
        assert output.calibrated_probability == 0.5
        assert output.confidence == 0.0

    def test_predictor_handles_invalid_features(self):
        """Test predictor handles invalid feature arrays."""
        predictor = AcceptancePredictor(
            model_path=Path("/nonexistent/model.joblib"),
            calibration_path=Path("/nonexistent/calibration.joblib"),
        )
        
        # Invalid features (wrong shape, NaN, etc.)
        features = np.array([np.nan, np.inf, -1.0])
        output = predictor.predict_probability(features)

        # Should return fallback
        assert isinstance(output, MLPredictionOutput)
        assert 0.0 <= output.raw_probability <= 1.0
        assert 0.0 <= output.calibrated_probability <= 1.0


class TestRiskPredictorFallback:
    """Test RiskPredictor with missing models."""

    def test_predictor_fallback_when_model_missing(self):
        """Test fallback when model is not available."""
        predictor = RiskPredictor(
            model_path=Path("/nonexistent/model.joblib"),
            calibration_path=Path("/nonexistent/calibration.joblib"),
        )
        
        features = np.array([1.0, 0.5, 4.0, 0.9, 0.7, 2.0, 100.0, 2.0, 0.7])
        output, risk_factors = predictor.predict_risk(features)

        # Should return fallback probabilities and empty factors
        assert isinstance(output, MLPredictionOutput)
        assert output.raw_probability == 0.0
        assert output.calibrated_probability == 0.0
        assert output.confidence == 0.0
        assert risk_factors == {}

    def test_predictor_returns_risk_factors(self):
        """Test that risk factors dict is returned."""
        predictor = RiskPredictor(
            model_path=Path("/nonexistent/model.joblib"),
            calibration_path=Path("/nonexistent/calibration.joblib"),
        )
        
        features = np.array([1.0, 0.5, 4.0, 0.9, 0.7, 2.0, 100.0, 2.0, 0.7])
        output, risk_factors = predictor.predict_risk(features)

        # Should return dict (even if empty)
        assert isinstance(risk_factors, dict)


class TestScoringStability:
    """Test score calculation stability."""

    def test_score_clamping_logic(self):
        """Test that scores are properly clamped."""
        from app.services.matching_engine import _safe_clamp, _calculate_final_score

        # Test clamping
        assert _safe_clamp(1.5) == 1.0
        assert _safe_clamp(-0.1) == 0.0
        assert _safe_clamp(0.5) == 0.5

        # Test with NaN/inf
        assert 0.0 <= _safe_clamp(np.nan) <= 1.0
        assert 0.0 <= _safe_clamp(np.inf) <= 1.0
        assert 0.0 <= _safe_clamp(-np.inf) <= 1.0

    def test_final_score_calculation(self):
        """Test final score blending with safety."""
        from app.services.matching_engine import _calculate_final_score

        # Normal case
        score = _calculate_final_score(
            rule_score=70.0,
            ml_probability=0.8,
            risk_probability=0.1,
        )
        assert 0.0 <= score <= 100.0
        
        # Expected: 0.7 * 70 + 0.3 * 0.8 - 0.1 * 15 = 49 + 0.24 - 1.5 = 47.74
        assert 47.0 <= score <= 48.0

    def test_final_score_with_extreme_values(self):
        """Test score calculation with extreme values."""
        from app.services.matching_engine import _calculate_final_score

        # Very high risk
        score = _calculate_final_score(
            rule_score=100.0,
            ml_probability=1.0,
            risk_probability=1.0,
        )
        assert 0.0 <= score <= 100.0
        
        # Very low values
        score = _calculate_final_score(
            rule_score=0.0,
            ml_probability=0.0,
            risk_probability=0.0,
        )
        assert 0.0 <= score <= 100.0

    def test_final_score_with_invalid_values(self):
        """Test score calculation with NaN/inf."""
        from app.services.matching_engine import _calculate_final_score

        # NaN handling
        score = _calculate_final_score(
            rule_score=np.nan,
            ml_probability=0.5,
            risk_probability=0.1,
        )
        assert np.isfinite(score)
        assert 0.0 <= score <= 100.0

        # Inf handling
        score = _calculate_final_score(
            rule_score=np.inf,
            ml_probability=0.5,
            risk_probability=0.1,
        )
        assert np.isfinite(score)
        assert 0.0 <= score <= 100.0
