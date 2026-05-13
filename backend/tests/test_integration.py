import pytest

from app.schemas.job import JobBase
from app.schemas.worker import WorkerResponse
from app.schemas.match import WorkerScore, MatchExplanation
from app.services.matching_engine import rank_candidates
from app.services.decision_engine import select_recommended_workers


class TestIntegration:
    def test_full_match_flow_returns_results(self):
        job = JobBase(
            id=1,
            title="Test Job",
            description="Test delivery",
            required_skills=["driving", "navigation"],
            latitude=40.0,
            longitude=-74.0,
            budget=100.0,
            urgency=3,
        )

        workers = [
            WorkerResponse(
                id=101,
                name="Alice",
                skills=["driving", "customer service"],
                distance_km=4.2,
                skill_overlap=0.5,
                rating=4.8,
                completion_rate=0.92,
                disputes=0,
                verified=True,
                latitude=40.01,
                longitude=-74.01,
                availability=0.9,
            ),
            WorkerResponse(
                id=102,
                name="Bob",
                skills=["navigation", "delivery"],
                distance_km=7.3,
                skill_overlap=0.75,
                rating=4.2,
                completion_rate=0.8,
                disputes=1,
                verified=True,
                latitude=40.05,
                longitude=-74.05,
                availability=0.7,
            ),
        ]

        results = rank_candidates(job, workers)

        assert len(results) > 0
        assert isinstance(results[0], WorkerScore)
        assert hasattr(results[0], 'final_score')
        assert hasattr(results[0], 'rule_score')
        assert hasattr(results[0], 'ml_probability')
        assert hasattr(results[0], 'confidence')

        # Check that results are sorted by final_score descending
        scores = [r.final_score for r in results]
        assert scores == sorted(scores, reverse=True)

    def test_decision_engine_recommends_workers(self):
        """Test multi-worker selection logic."""
        workers = [
            WorkerScore(
                worker_id=1,
                final_score=0.9,
                rule_score=0.85,
                ml_probability=0.88,
                risk_penalty=0.05,
                confidence=0.80,
                trust_score=0.75,
                profile_completeness=0.90,
                explanation=MatchExplanation(strengths=["great"], warnings=[]),
                metadata={},
            ),
            WorkerScore(
                worker_id=2,
                final_score=0.75,
                rule_score=0.70,
                ml_probability=0.75,
                risk_penalty=0.10,
                confidence=0.70,
                trust_score=0.65,
                profile_completeness=0.80,
                explanation=MatchExplanation(strengths=["good"], warnings=[]),
                metadata={},
            ),
            WorkerScore(
                worker_id=3,
                final_score=0.5,
                rule_score=0.50,
                ml_probability=0.50,
                risk_penalty=0.20,
                confidence=0.50,
                trust_score=0.50,
                profile_completeness=0.60,
                explanation=MatchExplanation(strengths=[], warnings=["low score"]),
                metadata={},
            ),
        ]

        recommended = select_recommended_workers(workers, max_recommended=2, min_score_threshold=0.6)
        assert len(recommended) == 2
        assert recommended == [1, 2]

    def test_empty_worker_list(self):
        """Test handling of empty worker list."""
        job = JobBase(
            id=1,
            title="Test",
            description="Test",
            required_skills=["test"],
            latitude=0.0,
            longitude=0.0,
            budget=100.0,
            urgency=1,
        )
        
        results = rank_candidates(job, [])
        assert results == []

