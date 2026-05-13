import pytest
from fastapi.testclient import TestClient
from sqlalchemy.ext.asyncio import AsyncSession

from app.main import app
from app.schemas.feedback import FeedbackRequest


class TestFeedbackLoop:
    @pytest.mark.asyncio
    async def test_feedback_loop_integration(self, client: TestClient):
        """Test the complete feedback loop: match -> accept -> feedback -> trust update"""

        # Step 1: Run matching
        match_payload = {
            "job": {
                "id": 1,
                "title": "Test Job",
                "description": "Test delivery",
                "required_skills": ["driving", "navigation"],
                "latitude": 40.0,
                "longitude": -74.0,
                "budget": 100.0,
                "urgency": 3,
            },
            "workers": [
                {
                    "id": 101,
                    "name": "Alice",
                    "skills": ["driving", "customer service"],
                    "distance_km": 4.2,
                    "skill_overlap": 0.5,
                    "rating": 4.8,
                    "completion_rate": 0.92,
                    "disputes": 0,
                    "verified": True,
                    "latitude": 40.01,
                    "longitude": -74.01,
                    "availability": 0.9,
                }
            ],
        }

        response = client.post("/api/v1/match", json=match_payload)
        assert response.status_code == 200
        match_result = response.json()
        assert len(match_result["matches"]) > 0

        top_match = match_result["matches"][0]
        worker_id = top_match["worker_id"]

        # Step 2: Accept the worker
        accept_payload = {
            "job_id": 1,
            "worker_id": worker_id,
        }
        response = client.post("/api/v1/match/accept", json=accept_payload)
        assert response.status_code == 200
        accept_result = response.json()
        assert accept_result["accepted"] is True
        match_log_id = accept_result["match_log_id"]

        # Step 3: Submit feedback
        feedback_payload = FeedbackRequest(
            match_log_id=match_log_id,
            completed=True,
            dispute_occurred=False,
            employer_rating=5.0,
            worker_rating=4.8,
        )

        response = client.post("/api/v1/feedback/", json=feedback_payload.model_dump())
        assert response.status_code == 200
        feedback_result = response.json()
        assert feedback_result["completed"] is True
        assert feedback_result["dispute_occurred"] is False

        # Step 4: Verify trust score was updated (would need DB check in real test)
        # For now, just check the response includes updated trust
        assert "worker_updated_trust" in feedback_result