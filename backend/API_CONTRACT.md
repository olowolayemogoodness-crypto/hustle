# Hustle Backend API Contract

## Core Match Endpoint

### `POST /api/v1/match`
**Request:**
```json
{
  "job": {
    "id": 1,
    "title": "string",
    "description": "string",
    "required_skills": ["string"],
    "latitude": 40.0,
    "longitude": -74.0,
    "budget": 100.0,
    "urgency": 3
  },
  "workers": [
    {
      "id": 101,
      "name": "string",
      "skills": ["string"],
      "distance_km": 4.2,
      "skill_overlap": 0.5,
      "rating": 4.8,
      "completion_rate": 0.92,
      "disputes": 0,
      "verified": true,
      "latitude": 40.01,
      "longitude": -74.01,
      "availability": 0.9
    }
  ]
}
```

**Response (200 OK):**
```json
{
  "job_id": "string",
  "ranked_workers": [
    {
      "worker_id": "string or int",
      "final_score": 0.97,
      "rule_score": 0.97,
      "ml_probability": 0.985,
      "risk_penalty": 0.0,
      "confidence": 0.962,
      "trust_score": 0.5,
      "profile_completeness": 0.0,
      "explanation": {
        "strengths": ["string"],
        "warnings": ["string"]
      },
      "metadata": {}
    }
  ],
  "recommended_worker_ids": [101, 102]
}
```

## Match Lifecycle

### `POST /api/v1/match/accept`
**Request:**
```json
{
  "job_id": "string or int",
  "worker_id": "string or int"
}
```

**Response (200 OK):**
```json
{
  "match_log_id": "string",
  "accepted": true
}
```

### `POST /api/v1/match/status`
**Request:**
```json
{
  "match_log_id": "string",
  "status": "viewed | selected | archived"
}
```

**Response (200 OK):**
```json
{
  "match_log_id": "string",
  "status": "viewed | selected | archived",
  "message": "string"
}
```

### `GET /api/v1/match/history/{job_id}`
**Response (200 OK):**
```json
{
  "job_id": "string",
  "matches": [
    {
      "worker_id": "string",
      "final_score": 0.97,
      "rule_score": 0.97,
      "ml_probability": 0.985,
      "risk_penalty": 0.0,
      "confidence": 0.962,
      "status": "ranked",
      "accepted": false,
      "completed": false,
      "dispute_occurred": false,
      "employer_rating": null,
      "worker_rating": null,
      "created_at": "string",
      "updated_at": "string"
    }
  ]
}
```

## Feedback Endpoint

### `POST /api/v1/feedback/`
**Request:**
```json
{
  "match_log_id": "string",
  "completed": true,
  "dispute_occurred": false,
  "employer_rating": 5.0,
  "worker_rating": 4.8
}
```

**Response (200 OK):**
```json
{
  "match_log_id": "string",
  "message": "Feedback recorded successfully"
}
```

## Key Schema Changes

- **MatchResponse**: Removed redundant `matches` field (use `ranked_workers` instead)
- **WorkerScore.worker_id**: Supports both `str | int` (UUID or legacy numeric ID)
- **AcceptMatchRequest**: Flexible ID types for `job_id` and `worker_id`
- **MatchHistoryResponse**: Contains structured `matches` array with full match log details

## Error Handling

- **400 Bad Request**: Invalid job_id format or validation errors
- **404 Not Found**: Match log or match status update target not found
- **500 Internal Server Error**: Database or ML model failures (logged, not exposed to client)

## Database Auto-Creation

Tables are automatically created at startup via `init_models()` called in app lifespan:
- `jobs`
- `users`
- `worker_profiles`
- `employer_profiles`
- `match_logs`
- `applications`
