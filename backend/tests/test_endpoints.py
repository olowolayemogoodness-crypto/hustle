match_payload = {
    'job': {
        'id': 1,
        'title': 'Delivery',
        'description': 'Deliver package',
        'required_skills': ['driving', 'navigation'],
        'latitude': 40.0,
        'longitude': -74.0,
        'budget': 100.0,
        'urgency': 3,
    },
    'workers': [
        {
            'id': 101,
            'name': 'Alice',
            'skills': ['driving', 'customer service'],
            'distance_km': 4.2,
            'skill_overlap': 0.5,
            'rating': 4.8,
            'completion_rate': 0.92,
            'disputes': 0,
            'verified': True,
            'latitude': 40.01,
            'longitude': -74.01,
            'availability': 0.9,
        },
        {
            'id': 102,
            'name': 'Bob',
            'skills': ['navigation', 'delivery'],
            'distance_km': 7.3,
            'skill_overlap': 0.75,
            'rating': 4.2,
            'completion_rate': 0.8,
            'disputes': 1,
            'verified': True,
            'latitude': 40.05,
            'longitude': -74.05,
            'availability': 0.7,
        },
    ],
}

def test_root_endpoint(client):
    response = client.get("/")
    assert response.status_code == 200
    assert "message" in response.json()


def test_health_endpoints_exist(client):
    live = client.get("/health/live")
    ready = client.get("/health/ready")
    assert live.status_code == 200
    assert ready.status_code in {200, 503}


def test_match_endpoint_returns_ranked_workers(client):
    response = client.post("/api/v1/match", json=match_payload)
    assert response.status_code == 200
    result = response.json()
    assert isinstance(result.get("ranked_workers"), list)
    assert isinstance(result.get("recommended_worker_ids"), list)


def test_match_accept_and_status_history_workflow(client):
    response = client.post("/api/v1/match", json=match_payload)
    assert response.status_code == 200
    result = response.json()
    assert result["ranked_workers"]
    worker_id = result["ranked_workers"][0]["worker_id"]

    accept_resp = client.post("/api/v1/match/accept", json={"job_id": 1, "worker_id": worker_id})
    assert accept_resp.status_code in {200, 404}

    status_resp = client.post("/api/v1/match/status", json={"match_log_id": f"1-{worker_id}", "status": "viewed"})
    assert status_resp.status_code in {200, 404}

    history_resp = client.get("/api/v1/match/history/1")
    assert history_resp.status_code in {200, 400}


def test_feedback_endpoint_is_available(client):
    response = client.post("/api/v1/feedback/", json={})
    assert response.status_code in {422, 400}


def test_auth_and_wallet_routes_are_registered(client):
    assert client.post("/api/v1/auth/otp/send", json={}).status_code == 422
    assert client.post("/api/v1/auth/role", json={}).status_code == 401
    assert client.get("/api/v1/wallet/balance").status_code == 401
    assert client.get("/api/v1/wallet/transactions").status_code == 401
    assert client.post("/api/v1/wallet/lookup", json={}).status_code == 401
    assert client.post("/api/v1/wallet/withdraw", json={}).status_code == 401


def test_webhook_route_requires_signature(client):
    response = client.post("/api/v1/webhook/squad", json={})
    assert response.status_code == 400
