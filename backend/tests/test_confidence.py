import pytest

from app.ml.confidence import calculate_confidence


class TestConfidenceEngine:
    def test_high_score_consistency_high_confidence(self):
        features = {
            "skill_overlap": 1.0,
            "trust_score": 0.9,
            "completion_rate": 0.95,
            "availability_weighted": 0.9,
            "profile_completeness": 0.9,
        }
        confidence = calculate_confidence(features)
        assert confidence > 0.8  # High consistency should give high confidence

    def test_noisy_inputs_low_confidence(self):
        features = {
            "skill_overlap": 0.2,
            "trust_score": 0.3,
            "completion_rate": 0.4,
            "availability_weighted": 0.5,
            "profile_completeness": 0.3,
        }
        confidence = calculate_confidence(features)
        assert confidence < 0.5  # Noisy inputs should give low confidence

    def test_perfect_match_max_confidence(self):
        features = {
            "skill_overlap": 1.0,
            "trust_score": 1.0,
            "completion_rate": 1.0,
            "availability_weighted": 1.0,
            "profile_completeness": 1.0,
        }
        confidence = calculate_confidence(features)
        assert confidence == 1.0

    def test_minimal_features_min_confidence(self):
        features = {
            "skill_overlap": 0.0,
            "trust_score": 0.0,
            "completion_rate": 0.0,
            "availability_weighted": 0.0,
            "profile_completeness": 0.0,
        }
        confidence = calculate_confidence(features)
        assert confidence == 0.0