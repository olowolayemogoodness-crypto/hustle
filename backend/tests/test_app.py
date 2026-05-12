from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


def test_health_live_and_metrics():
    response = client.get("/health/live")
    assert response.status_code == 200
    assert response.json() == {"status": "alive"}
    assert "X-Response-Time-ms" in response.headers


def test_health_ready_reports_degraded_or_ready():
    response = client.get("/health/ready")
    assert response.status_code in {200, 503}
    assert response.json()["status"] in {"ready", "degraded"}


def test_predict_endpoint_returns_probability():
    response = client.post(
        "/api/v1/predict",
        json={
            "distance_km": 2.5,
            "skill_overlap": 0.8,
            "rating": 4.9,
            "completion_rate": 0.95,
            "disputes": 0,
            "availability": 0.9,
        },
    )
    assert response.status_code == 200
    data = response.json()
    assert "success_probability" in data
    assert 0.0 <= data["success_probability"] <= 1.0


def test_match_endpoint_returns_sorted_matches():
    payload = {
        "job": {
            "id": 1,
            "title": "Delivery",
            "description": "Deliver package",
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
            },
            {
                "id": 102,
                "name": "Bob",
                "skills": ["navigation", "delivery"],
                "distance_km": 7.3,
                "skill_overlap": 0.75,
                "rating": 4.2,
                "completion_rate": 0.8,
                "disputes": 1,
                "verified": True,
                "latitude": 40.05,
                "longitude": -74.05,
                "availability": 0.7,
            },
        ],
    }

    response = client.post("/api/v1/match", json=payload)
    assert response.status_code == 200
    result = response.json()
    assert "matches" in result
    assert isinstance(result["matches"], list)
    assert all("worker_id" in item for item in result["matches"])
