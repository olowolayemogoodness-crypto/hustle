"""
Endpoint compatibility verification tests.
Ensures all API contracts remain unchanged with Phase 2.5 changes.
"""
import uuid
from types import SimpleNamespace

import pytest

from app.schemas.match import (
    MatchRequest,
    MatchResponse,
    AcceptMatchRequest,
    AcceptMatchResponse,
    MatchHistoryEntry,
    MatchHistoryResponse,
    MatchStatusUpdate,
    MatchStatusResponse,
)
from app.schemas.job import JobBase
from app.schemas.worker import WorkerResponse


class TestEndpointContracts:
    """Verify endpoint request/response schemas remain unchanged."""

    def test_match_request_schema_unchanged(self):
        """MatchRequest must have job and workers fields."""
        job = JobBase(
            id=1,
            title="Test Job",
            description="A test job",
            budget=100.0,
            urgency=1,
            required_skills=["Python", "FastAPI"],
            latitude=40.0,
            longitude=-74.0,
        )
        workers = [
            WorkerResponse(
                id=str(uuid.uuid4()),
                name="Worker 1",
                distance_km=5.0,
                skills=["Python", "FastAPI"],
                rating=4.5,
                completed_jobs=5,
                completion_rate=0.95,
                disputes=0,
                verified=True,
                latitude=40.0,
                longitude=-74.0,
                availability=0.8,
                trust_score=0.8,
            )
        ]

        request = MatchRequest(job=job, workers=workers)
        assert request.job is not None
        assert len(request.workers) == 1

    def test_match_response_schema_unchanged(self):
        """MatchResponse must have job_id, ranked_workers, recommended_worker_ids."""
        response = MatchResponse(
            job_id=str(uuid.uuid4()),
            ranked_workers=[],
            recommended_worker_ids=[],
        )
        assert "job_id" in response.__dict__
        assert "ranked_workers" in response.__dict__
        assert "recommended_worker_ids" in response.__dict__

    def test_accept_match_request_unchanged(self):
        """AcceptMatchRequest must have job_id and worker_id."""
        request = AcceptMatchRequest(
            job_id=str(uuid.uuid4()),
            worker_id=str(uuid.uuid4()),
        )
        assert request.job_id is not None
        assert request.worker_id is not None

    def test_accept_match_response_unchanged(self):
        """AcceptMatchResponse must have match_log_id and accepted."""
        response = AcceptMatchResponse(
            match_log_id=str(uuid.uuid4()),
            accepted=True,
        )
        assert response.match_log_id is not None
        assert response.accepted is True

    def test_match_history_entry_schema_extended_safely(self):
        """MatchHistoryEntry has new fields but all are optional/backward compatible."""
        entry = MatchHistoryEntry(
            worker_id=str(uuid.uuid4()),
            final_score=0.75,
            rule_score=0.80,
            ml_probability=0.70,
            risk_penalty=0.05,
            confidence=0.8,
            status="ranked",
            accepted=False,
            completed=False,
            dispute_occurred=False,
            employer_rating=None,
            worker_rating=None,
            completion_risk_probability=0.1,  # New field
            risk_factors=None,  # New field
        )
        assert entry.worker_id is not None
        assert entry.final_score == 0.75
        assert entry.completion_risk_probability == 0.1

    def test_match_history_response_unchanged(self):
        """MatchHistoryResponse must have job_id and matches."""
        response = MatchHistoryResponse(
            job_id=str(uuid.uuid4()),
            matches=[],
        )
        assert response.job_id is not None
        assert len(response.matches) == 0

    def test_match_status_update_unchanged(self):
        """MatchStatusUpdate must have match_log_id and status."""
        update = MatchStatusUpdate(
            match_log_id=str(uuid.uuid4()),
            status="viewed",
        )
        assert update.match_log_id is not None
        assert update.status == "viewed"

    def test_match_status_response_unchanged(self):
        """MatchStatusResponse must have match_log_id, status, and message."""
        response = MatchStatusResponse(
            match_log_id=str(uuid.uuid4()),
            status="viewed",
            message="Match marked as viewed",
        )
        assert response.match_log_id is not None
        assert response.status == "viewed"
        assert response.message is not None


class TestEndpointBehavior:
    """Verify endpoint behavior remains consistent."""

    def test_matching_engine_returns_consistent_structure(self):
        """Matching engine must return WorkerScore with all required fields."""
        from app.services.matching_engine import rank_candidates

        job = JobBase(
            id=str(uuid.uuid4()),
            title="Test Job",
            description="A test job",
            budget=100.0,
            urgency=1,
            required_skills=["Python"],
        )
        workers = [
            WorkerResponse(
                id=str(uuid.uuid4()),
                name="Worker 1",
                distance_km=5.0,
                skills=["Python"],
                rating=4.5,
                completed_jobs=5,
                completion_rate=0.95,
                disputes=0,
                verified=True,
                latitude=40.0,
                longitude=-74.0,
                availability=0.8,
                trust_score=0.8,
            )
        ]

        ranked = rank_candidates(job, workers)

        # Should return list of WorkerScore
        assert isinstance(ranked, list)
        if ranked:
            worker_score = ranked[0]
            assert hasattr(worker_score, "worker_id")
            assert hasattr(worker_score, "final_score")
            assert hasattr(worker_score, "rule_score")
            assert hasattr(worker_score, "ml_probability")
            assert hasattr(worker_score, "risk_penalty")
            assert hasattr(worker_score, "confidence")
            assert hasattr(worker_score, "explanation")
            assert hasattr(worker_score, "metadata")

    def test_matching_engine_scores_are_valid(self):
        """Matching engine must produce valid scores."""
        from app.services.matching_engine import rank_candidates

        job = JobBase(
            id=str(uuid.uuid4()),
            title="Test Job",
            description="A test job",
            budget=100.0,
            urgency=1,
            required_skills=["Python"],
        )
        workers = [
            WorkerResponse(
                id=str(uuid.uuid4()),
                name="Worker 1",
                distance_km=5.0,
                skills=["Python"],
                rating=4.5,
                completed_jobs=5,
                completion_rate=0.95,
                disputes=0,
                verified=True,
                latitude=40.0,
                longitude=-74.0,
                availability=0.8,
                trust_score=0.8,
            )
        ]

        ranked = rank_candidates(job, workers)

        for worker_score in ranked:
            # All scores should be valid (normalized to 0-1)
            assert 0.0 <= worker_score.final_score <= 1.0
            assert 0.0 <= worker_score.rule_score <= 1.0
            assert 0.0 <= worker_score.ml_probability <= 1.0
            assert 0.0 <= worker_score.risk_penalty <= 1.0
            assert 0.0 <= worker_score.confidence <= 1.0

    def test_matching_engine_handles_empty_workers(self):
        """Matching engine should gracefully handle empty worker list."""
        from app.services.matching_engine import rank_candidates

        job = JobBase(
            id=str(uuid.uuid4()),
            title="Test Job",
            description="A test job",
            budget=100.0,
            urgency=1,
            required_skills=["Python"],
        )
        workers = []

        ranked = rank_candidates(job, workers)
        assert ranked == []

    def test_matching_engine_handles_no_matching_workers(self):
        """Matching engine should filter workers below threshold."""
        from app.services.matching_engine import rank_candidates
        from app.core.config import settings

        job = JobBase(
            id=str(uuid.uuid4()),
            title="Test Job",
            description="A test job",
            budget=100.0,
            urgency=1,
            required_skills=["Rust"],  # Worker doesn't have this skill
        )
        workers = [
            WorkerResponse(
                id=str(uuid.uuid4()),
                name="Worker 1",
                distance_km=100.0,  # Very far
                skills=["Python"],  # No Rust
                rating=2.0,  # Low rating
                completed_jobs=0,
                completion_rate=0.5,  # Low completion
                disputes=0,
                verified=True,
                latitude=40.0,
                longitude=-74.0,
                availability=0.5,
                trust_score=0.2,  # Low trust
            )
        ]

        ranked = rank_candidates(job, workers)
        # May be empty or below threshold
        for worker_score in ranked:
            assert worker_score.final_score >= settings.match_threshold
