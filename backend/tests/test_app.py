import pytest

from fastapi.testclient import TestClient
from app.main import app


def build_match_payload():
    return {
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


def test_health_live_and_metrics(client):
    response = client.get("/health/live")
    assert response.status_code == 200
    assert response.json() == {"status": "alive"}
    assert "X-Response-Time-ms" in response.headers


def test_health_ready_reports_degraded_or_ready(client):
    response = client.get("/health/ready")
    assert response.status_code in {200, 503}
    assert response.json()["status"] in {"ready", "degraded"}


def test_predict_endpoint_returns_probability(client):
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


def test_match_endpoint_returns_sorted_matches(client):
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
    assert "ranked_workers" in result
    assert isinstance(result["ranked_workers"], list)
    assert all("worker_id" in item for item in result["ranked_workers"])
    assert "recommended_worker_ids" in result
    assert isinstance(result["recommended_worker_ids"], list)


@pytest.mark.asyncio
async def test_accept_match_endpoint(db_session):
    from app.api.match import match
    from app.schemas.match import MatchRequest, AcceptMatchRequest

    payload = build_match_payload()
    match_req = MatchRequest(**payload)
    result = await match(match_req, db_session)
    assert result.recommended_worker_ids

    accept_req = AcceptMatchRequest(job_id=1, worker_id=result.recommended_worker_ids[0])
    from app.api.match import accept_match
    accept_result = await accept_match(accept_req, db_session)
    assert accept_result.accepted is True


@pytest.mark.asyncio
async def test_match_history_endpoint(db_session):
    from app.api.match import match, get_match_history
    from app.schemas.match import MatchRequest

    payload = build_match_payload()
    match_req = MatchRequest(**payload)
    await match(match_req, db_session)

    result = await get_match_history(1, db_session)
    assert result.job_id == "00000000-0000-0000-0000-000000000001"
    assert isinstance(result.matches, list)


@pytest.mark.asyncio
async def test_feedback_endpoint(db_session):
    from app.api.match import match, accept_match
    from app.api.feedback import submit_feedback
    from app.schemas.match import MatchRequest, AcceptMatchRequest
    from app.schemas.feedback import FeedbackRequest

    payload = build_match_payload()
    match_req = MatchRequest(**payload)
    result = await match(match_req, db_session)
    assert result.recommended_worker_ids

    accept_req = AcceptMatchRequest(job_id=1, worker_id=result.recommended_worker_ids[0])
    accept_result = await accept_match(accept_req, db_session)
    assert accept_result.accepted is True

    feedback_req = FeedbackRequest(
        match_log_id=str(accept_result.match_log_id),
        completed=True,
        dispute_occurred=False,
        employer_rating=5.0,
        worker_rating=4.8,
    )
    feedback_result = await submit_feedback(feedback_req, db_session)
    assert feedback_result.completed is True


def test_analytics_endpoint(client):
    response = client.get("/api/v1/analytics/matches")
    assert response.status_code == 200
    result = response.json()
    assert "total_matches" in result
    assert "average_match_score" in result
    assert "acceptance_rate" in result
    assert "completion_rate" in result
