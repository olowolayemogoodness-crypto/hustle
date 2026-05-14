import os
import asyncio
from pathlib import Path
from fastapi.testclient import TestClient

DB_PATH = Path('sample_test.db').resolve()
if DB_PATH.exists():
    try:
        DB_PATH.unlink()
    except Exception:
        pass

os.environ['HUSTLE_DATABASE_URL'] = f'sqlite+aiosqlite:///{DB_PATH.as_posix()}'
os.environ['HUSTLE_TESTING'] = '1'

from app.db.init_db import init_models
from app.main import app

# Initialize DB and then close the event loop properly
async def main():
    await init_models()

asyncio.run(main())

# Create a new event loop for TestClient
client = TestClient(app)

print('ROOT', client.get('/').json())
print('LIVE', client.get('/health/live').status_code, client.get('/health/live').json())
print('READY', client.get('/health/ready').status_code, client.get('/health/ready').json())

predict_payload = {
    'distance_km': 2.5,
    'skill_overlap': 0.8,
    'rating': 4.9,
    'completion_rate': 0.95,
    'disputes': 0,
    'availability': 0.9,
}
print('PREDICT', client.post('/api/v1/predict', json=predict_payload).json())

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

match_resp = client.post('/api/v1/match', json=match_payload)
print('MATCH', match_resp.status_code, match_resp.json())
match_json = match_resp.json()
ranked_workers = match_json.get('ranked_workers', [])
worker_id = ranked_workers[0]['worker_id'] if ranked_workers else 101
accept_resp = client.post('/api/v1/match/accept', json={'job_id': 1, 'worker_id': worker_id})
print('ACCEPT', accept_resp.status_code, accept_resp.json())

status_resp = client.post('/api/v1/match/status', json={'match_log_id': f'1-{worker_id}', 'status': 'viewed'})
print('STATUS', status_resp.status_code, status_resp.json())

history_resp = client.get('/api/v1/match/history/1')
print('HISTORY', history_resp.status_code, history_resp.json())

feedback_resp = client.post('/api/v1/feedback/', json={
    'match_log_id': str(accept_resp.json().get('match_log_id')),
    'completed': True,
    'dispute_occurred': False,
    'employer_rating': 5.0,
    'worker_rating': 4.8,
})
print('FEEDBACK', feedback_resp.status_code, feedback_resp.json())

analytics_resp = client.get('/api/v1/analytics/matches')
print('ANALYTICS', analytics_resp.status_code, analytics_resp.json())
