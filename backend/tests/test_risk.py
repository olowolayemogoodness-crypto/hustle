import pytest

from app.ml.risk import calculate_risk_penalty


class TestRiskEngine:
    def test_high_disputes_high_risk(self):
        features = {
            "disputes": 5,
            "completion_rate": 0.9,
            "availability": 0.8,
            "trust_score": 0.8,
            "profile_completeness": 0.8,
            "is_verified": True,
        }
        penalty = calculate_risk_penalty(features)
        assert penalty > 0.1  # Should have significant penalty for high disputes

    def test_clean_worker_low_risk(self):
        features = {
            "disputes": 0,
            "completion_rate": 0.95,
            "availability": 0.9,
            "trust_score": 0.9,
            "profile_completeness": 0.9,
            "is_verified": True,
        }
        penalty = calculate_risk_penalty(features)
        assert penalty == 0.0  # Clean worker should have no penalty

    def test_low_completion_rate_penalty(self):
        features = {
            "disputes": 0,
            "completion_rate": 0.5,
            "availability": 0.9,
            "trust_score": 0.8,
            "profile_completeness": 0.8,
            "is_verified": True,
        }
        penalty = calculate_risk_penalty(features)
        assert penalty > 0.1  # Low completion rate should add penalty

    def test_unverified_penalty(self):
        features = {
            "disputes": 0,
            "completion_rate": 0.9,
            "availability": 0.9,
            "trust_score": 0.8,
            "profile_completeness": 0.8,
            "is_verified": False,
        }
        penalty = calculate_risk_penalty(features)
        assert penalty >= 0.05  # Unverified should add penalty