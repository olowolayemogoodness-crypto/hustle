import pytest

from app.ml.feature_engineering import compute_skill_overlap, extract_worker_features
from app.schemas.job import JobBase


class TestFeatureEngineering:
    def test_skill_overlap_empty_skills(self):
        assert compute_skill_overlap([], []) == 0.0
        assert compute_skill_overlap(["python"], []) == 0.0
        assert compute_skill_overlap([], ["python"]) == 0.0

    def test_skill_overlap_partial_overlap(self):
        assert compute_skill_overlap(["python", "django"], ["python", "flask"]) == 0.5
        assert compute_skill_overlap(["python", "django", "react"], ["python", "flask"]) == 0.3333333333333333

    def test_skill_overlap_full_overlap(self):
        assert compute_skill_overlap(["python"], ["python"]) == 1.0
        assert compute_skill_overlap(["python", "django"], ["python", "django"]) == 1.0

    def test_extract_worker_features_missing_rating(self):
        job = JobBase(
            id=1,
            title="Test Job",
            description="Test",
            required_skills=["python"],
            latitude=0.0,
            longitude=0.0,
            budget=100.0,
            urgency=1,
        )
        worker = {
            "id": 1,
            "skills": ["python"],
            "distance_km": 5.0,
            "rating": None,  # Missing rating
            "completion_rate": None,  # Missing completion_rate
            "disputes": 0,
            "verified": True,
            "latitude": 0.0,
            "longitude": 0.0,
            "availability": 1.0,
        }
        features = extract_worker_features(job, worker)
        assert features["rating"] == 2.5  # Should use fallback
        assert features["completion_rate"] == 0.5  # Should use fallback
        assert features["skill_overlap"] == 1.0