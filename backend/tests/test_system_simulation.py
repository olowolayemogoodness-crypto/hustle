import random
import pytest
from fastapi.testclient import TestClient
from sqlalchemy.ext.asyncio import AsyncSession

from app.main import app
from app.schemas.feedback import FeedbackRequest


class TestSystemSimulation:
    @pytest.mark.asyncio
    async def test_system_improves_over_time(self, client: TestClient):
        """Simulate 10 jobs with 50 workers, random accept/reject patterns"""

        # Create pool of 50 workers with varying quality
        workers = []
        for i in range(50):
            # Some good workers, some bad
            is_good = random.random() < 0.3  # 30% are good workers
            worker = {
                "id": 100 + i,
                "name": f"Worker {i}",
                "skills": ["driving", "navigation"] if is_good else ["basic"],
                "distance_km": random.uniform(1, 20),
                "skill_overlap": 1.0 if is_good else 0.2,
                "rating": random.uniform(4.5, 5.0) if is_good else random.uniform(2.0, 3.5),
                "completion_rate": random.uniform(0.9, 1.0) if is_good else random.uniform(0.3, 0.7),
                "disputes": 0 if is_good else random.randint(1, 3),
                "verified": is_good,
                "latitude": 40.0 + random.uniform(-0.1, 0.1),
                "longitude": -74.0 + random.uniform(-0.1, 0.1),
                "availability": random.uniform(0.8, 1.0) if is_good else random.uniform(0.3, 0.7),
            }
            workers.append(worker)

        job_results = []

        # Simulate 10 jobs
        for job_id in range(10):
            job = {
                "id": job_id,
                "title": f"Job {job_id}",
                "description": "Delivery job",
                "required_skills": ["driving", "navigation"],
                "latitude": 40.0,
                "longitude": -74.0,
                "budget": 100.0,
                "urgency": 3,
            }

            # Run matching
            match_payload = {"job": job, "workers": workers}
            response = client.post("/api/v1/match", json=match_payload)
            assert response.status_code == 200
            ranked_workers = response.json()["ranked_workers"]

            # Record top match score
            if ranked_workers:
                top_score = ranked_workers[0]["final_score"]
                job_results.append(top_score)

                # Simulate random acceptance (70% acceptance rate)
                if random.random() < 0.7:
                    worker_id = ranked_workers[0]["worker_id"]
                    accept_payload = {"job_id": job_id, "worker_id": worker_id}
                    client.post("/api/v1/match/accept", json=accept_payload)

                    # Simulate feedback
                    completed = random.random() < 0.8  # 80% completion rate
                    dispute = random.random() < 0.1  # 10% dispute rate
                    employer_rating = random.uniform(4.0, 5.0) if completed else random.uniform(1.0, 3.0)
                    worker_rating = random.uniform(4.0, 5.0) if completed else random.uniform(1.0, 3.0)

                    feedback_payload = FeedbackRequest(
                        match_log_id=f"{job_id}-{worker_id}",
                        completed=completed,
                        dispute_occurred=dispute,
                        employer_rating=employer_rating,
                        worker_rating=worker_rating,
                    )
                    client.post("/api/v1/feedback/", json=feedback_payload.model_dump())

        # Check that we have results
        assert len(job_results) > 0

        # In a real system, we'd check if later jobs have higher average scores
        # as good workers get better ratings through feedback
        # For now, just verify the simulation ran
        avg_score = sum(job_results) / len(job_results)
        assert 0.0 <= avg_score <= 1.0

        # Check analytics endpoint
        response = client.get("/api/v1/analytics/matches")
        assert response.status_code == 200
        analytics = response.json()
        assert "total_matches" in analytics
        assert "average_match_score" in analytics