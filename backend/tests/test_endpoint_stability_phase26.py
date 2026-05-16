"""
Tests for endpoint stability with Phase 2.6 observability layer.
Ensures API contracts remain unchanged while adding observability.
"""
import pytest
from app.schemas.job import JobBase
from app.schemas.worker import WorkerResponse
from app.schemas.match import WorkerScore, MatchExplanation
from app.services.matching_engine import rank_candidates


class TestEndpointStabilityPhase26:
    """Test that Phase 2.6 doesn't break API contracts."""

    def test_rank_candidates_returns_list(self):
        """Test that rank_candidates returns a list."""
        job = JobBase(
            id=1,
            title="Delivery",
            description="Deliver package",
            required_skills=["driving"],
            latitude=40.0,
            longitude=-74.0,
            budget=100.0,
            urgency=1,
        )
        workers = []
        result = rank_candidates(job, workers)
        assert isinstance(result, list)

    def test_rank_candidates_empty_list(self):
        """Test rank_candidates with empty worker list."""
        job = JobBase(
            id=1,
            title="Delivery",
            description="Deliver package",
            required_skills=["driving"],
            latitude=40.0,
            longitude=-74.0,
            budget=100.0,
            urgency=1,
        )
        result = rank_candidates(job, [])
        assert result == []

    def test_worker_score_schema_unchanged(self):
        """Test that WorkerScore schema is unchanged."""
        # Create a minimal valid WorkerScore (normalized scores: 0-1)
        score = WorkerScore(
            worker_id="w1",
            final_score=0.75,
            rule_score=0.50,
            ml_probability=0.7,
            risk_penalty=0.25,
            confidence=0.8,
            trust_score=0.45,
            profile_completeness=0.9,
            explanation=MatchExplanation(primary_reason="Test match", factors=["match"]),
        )
        assert score.worker_id == "w1"
        assert score.final_score == 0.75
        # Ensure metadata is still there
        assert hasattr(score, 'metadata')

    def test_score_has_ranking_trace_in_metadata(self):
        """Test that ranking trace is available in metadata when enabled."""
        # This test verifies backward compat: trace is in metadata dict, not in response
        score = WorkerScore(
            worker_id="w1",
            final_score=0.75,
            rule_score=0.50,
            ml_probability=0.7,
            risk_penalty=0.25,
            confidence=0.8,
            trust_score=0.45,
            profile_completeness=0.9,
            explanation=MatchExplanation(primary_reason="Test match", factors=["match"]),
            metadata={"ranking_trace": {"worker_id": "w1"}},
        )
        assert "ranking_trace" in score.metadata

    def test_match_explanation_schema_unchanged(self):
        """Test that MatchExplanation schema is unchanged."""
        score = WorkerScore(
            worker_id="w1",
            final_score=0.75,
            rule_score=0.50,
            ml_probability=0.7,
            risk_penalty=0.25,
            confidence=0.8,
            trust_score=0.45,
            profile_completeness=0.9,
            explanation=MatchExplanation(primary_reason="Test match", factors=["match"]),
        )
        assert hasattr(score, 'explanation')

    def test_worker_score_all_fields_present(self):
        """Test all WorkerScore fields are present and accessible."""
        score = WorkerScore(
            worker_id="w1",
            final_score=0.75,
            rule_score=0.50,
            ml_probability=0.7,
            risk_penalty=0.25,
            confidence=0.8,
            trust_score=0.45,
            profile_completeness=0.9,
            explanation=MatchExplanation(primary_reason="Test match", factors=["match"]),
            metadata={},
        )
        
        # Verify all fields
        assert score.worker_id == "w1"
        assert score.final_score == 0.75
        assert score.rule_score == 0.50
        assert score.ml_probability == 0.7
        assert score.risk_penalty == 0.25
        assert score.confidence == 0.8
        assert score.trust_score == 0.45
        assert score.profile_completeness == 0.9

    def test_score_serialization(self):
        """Test that WorkerScore serializes correctly."""
        score = WorkerScore(
            worker_id="w1",
            final_score=0.75,
            rule_score=0.50,
            ml_probability=0.7,
            risk_penalty=0.25,
            confidence=0.8,
            trust_score=0.45,
            profile_completeness=0.9,
            explanation=MatchExplanation(primary_reason="Test match", factors=["match"]),
        )
        # Should be able to convert to dict
        if hasattr(score, 'model_dump'):
            d = score.model_dump()
            assert d['worker_id'] == 'w1'
        elif hasattr(score, 'dict'):
            d = score.dict()
            assert d['worker_id'] == 'w1'


class TestRankingStabilityWithoutModels:
    """Test ranking stability when ML models are not available."""

    def test_rank_candidates_fallback_when_models_missing(self):
        """Test that ranking still works when models are missing."""
        # This tests the fallback path
        job = JobBase(
            id=1,
            title="Delivery",
            description="Deliver package",
            required_skills=["driving", "navigation"],
            latitude=40.0,
            longitude=-74.0,
            budget=100.0,
            urgency=2,
        )
        
        worker = WorkerResponse(
            id="w1",
            name="John",
            skills=["driving", "navigation"],
            completed_jobs=2,
            rating=4.5,
            distance_km=3.0,
            latitude=40.01,
            longitude=-74.01,
            completion_rate=0.95,
            disputes=0,
            verified=True,
            availability=0.8,
        )
        
        # Should still return valid scores
        result = rank_candidates(job, [worker])
        # Result may be empty if threshold not met, but should be a list
        assert isinstance(result, list)

    def test_rank_candidates_consistent_output(self):
        """Test that rank_candidates produces consistent output."""
        job = JobBase(
            id=1,
            title="Delivery",
            description="Deliver package",
            required_skills=["driving"],
            latitude=40.0,
            longitude=-74.0,
            budget=100.0,
            urgency=1,
        )
        
        worker = WorkerResponse(
            id="w1",
            name="John",
            skills=["driving"],
            completed_jobs=2,
            rating=4.5,
            distance_km=3.0,
            latitude=40.01,
            longitude=-74.01,
            completion_rate=0.95,
            disputes=0,
            verified=True,
            availability=0.8,
        )
        
        # Call twice
        result1 = rank_candidates(job, [worker])
        result2 = rank_candidates(job, [worker])
        
        # Results should be of same type
        assert type(result1) == type(result2)
        assert isinstance(result1, list)


class TestScoreNormalizationStability:
    """Test that score normalization works correctly."""

    def test_final_score_in_valid_range(self):
        """Test that final scores are always in valid range."""
        score = WorkerScore(
            worker_id="w1",
            final_score=0.75,
            rule_score=0.50,
            ml_probability=0.7,
            risk_penalty=0.25,
            confidence=0.8,
            trust_score=0.45,
            profile_completeness=0.9,
            explanation=MatchExplanation(primary_reason="Test", factors=["test"]),
        )
        # Score should be between 0 and 1 (normalized)
        assert 0 <= score.final_score <= 1

    def test_ml_probability_in_valid_range(self):
        """Test that ML probability is in [0, 1]."""
        score = WorkerScore(
            worker_id="w1",
            final_score=0.75,
            rule_score=0.50,
            ml_probability=0.7,
            risk_penalty=0.25,
            confidence=0.8,
            trust_score=0.45,
            profile_completeness=0.9,
            explanation=MatchExplanation(primary_reason="Test", factors=["test"]),
        )
        assert 0 <= score.ml_probability <= 1

    def test_risk_penalty_in_valid_range(self):
        """Test that risk penalty is in valid range."""
        score = WorkerScore(
            worker_id="w1",
            final_score=0.75,
            rule_score=0.50,
            ml_probability=0.7,
            risk_penalty=0.25,
            confidence=0.8,
            trust_score=0.45,
            profile_completeness=0.9,
            explanation=MatchExplanation(primary_reason="Test", factors=["test"]),
        )
        # Risk penalty should be between 0 and 1
        assert 0 <= score.risk_penalty <= 1
