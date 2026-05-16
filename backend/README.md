# Hustle Backend — Complete Guide

## Overview

Hustle backend is a FastAPI-based matching and job platform MVP with ML-powered worker ranking, real-time feedback loops, and production-ready async database handling.

**Status:** MVP Complete ✅ | Tests: 76/94 passing | Latest: Phase 2.6 (Ranking Observability)

---

## Quick Start

### Setup
```bash
cd backend
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
alembic upgrade head
```

### Run server
```bash
python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### Run tests
```bash
pytest tests/ -v
```

---

## Architecture

### Directory Structure
```
app/
  ├── api/v1/endpoints/          # Route handlers
  ├── services/                  # Business logic (matching, feedback, events)
  ├── ml/                        # ML models & feature engineering
  ├── db/                        # Database models & session management
  ├── schemas/                   # Pydantic request/response models
  ├── core/                      # Config, logging, middleware, security
  └── models/                    # SQLAlchemy ORM models
db/
  └── migrations/                # Alembic version-controlled schema changes
tests/                           # Pytest test suite
requirements.txt                 # Python dependencies
```

### Core Layers
1. **API Layer** (`api/v1/`) — FastAPI routes, request validation, response formatting
2. **Service Layer** (`services/`) — Business logic (matching, ranking, feedback)
3. **ML Layer** (`ml/`) — Feature extraction, model inference, calibration (Platt Scaling)
4. **Data Layer** (`db/`) — SQLAlchemy ORM, async session management, migrations
5. **Schema Layer** (`schemas/`) — Pydantic models for type safety and validation

---

## API Endpoints

### Match Endpoint
**`POST /api/v1/match`** — Rank workers for a job

**Request:**
```json
{
  "job": {
    "id": 1,
    "title": "Delivery Driver",
    "description": "Same-day delivery",
    "required_skills": ["driving", "navigation"],
    "latitude": 40.0,
    "longitude": -74.0,
    "budget": 100.0,
    "urgency": 3
  },
  "workers": [{"id": 101, "name": "John", "skills": ["driving"], ...}]
}
```

**Response (200 OK):**
```json
{
  "job_id": "1",
  "ranked_workers": [
    {
      "worker_id": 101,
      "final_score": 0.85,
      "rule_score": 0.8,
      "ml_probability": 0.88,
      "risk_penalty": 0.03,
      "confidence": 0.9,
      "explanation": {"primary_reason": "...", "factors": [...]},
      "metadata": {"ranking_trace": {...}}
    }
  ],
  "recommended_worker_ids": [101, 102, 103]
}
```

### Accept Match
**`POST /api/v1/match/accept`** — Accept a ranked match

```json
{"job_id": "1", "worker_id": 101}
```

### Match Status
**`POST /api/v1/match/status`** — Update match state (viewed → selected)

**`GET /api/v1/match/history/{job_id}`** — Retrieve match history

### Feedback
**`POST /api/v1/feedback`** — Record completion and rating

```json
{"match_id": "uuid", "employer_rating": 5.0, "worker_rating": 4.5}
```

### Health & Analytics
- **`GET /healthz`** — Liveness probe
- **`GET /ready`** — Readiness probe
- **`GET /api/v1/analytics`** — Match counts, acceptance rates, completion rates

---

## ML Pipeline (Phase 2 — Phase 2.6)

### Phase 2: Risk Prediction
- **RiskPredictor** predicts completion risk from worker features
- Calibrated probability estimates prevent over/under-confidence
- Fallback: Returns base rate (5% risk) when model unavailable

### Phase 2.5: Calibration (Platt Scaling)
- **PlattScaler** transforms raw model outputs to probability estimates
- Handles insufficient data with Laplace smoothing
- Savepoints for reproducible predictions

### Phase 2.6: Ranking Trace & Observability
- **RankingTrace** captures all scoring decisions: rule-based, ML, risk penalty
- **RankingDecisionLogger** logs traces for audit and debugging
- Traces included in API response metadata when enabled (`enable_ranking_trace=true`)

### Feature Set
| Feature | Source | Range |
|---------|--------|-------|
| `distance_km` | Worker profile | 0–1000 |
| `skill_overlap` | Rule-based matching | 0–1 |
| `rating` | Worker profile | 0–5 |
| `completion_rate` | Historical | 0–1 |
| `trust_score` | Feedback loop | 0–1 |
| `completed_jobs` | Historical | 0+ |
| `budget` | Job posting | 0+ |
| `urgency` | Job posting | 1–5 |

### Scoring Formula
```
rule_score = distance_bonus + skill_match + rating_bonus  [0–100]
ml_probability = AcceptancePredictor(features)  [0–1]
risk_probability = RiskPredictor(features)  [0–1]
risk_penalty = risk_probability * 0.15  [0–0.15]
final_score = 0.7 * (rule_score/100) + 0.3 * ml_probability - risk_penalty  [0–1]
```

---

## Database Schema

### Tables
- **users** — Employer and worker accounts
- **employer_profiles** — Employer-specific fields (company name, license)
- **worker_profiles** — Worker-specific fields (bio, experience, rating)
- **jobs** — Job postings (title, budget, urgency, geo)
- **applications** — Worker applications (status, timestamp)
- **match_logs** — Ranking records (scores, acceptance, completion)
- **feedback** — Rating and completion feedback (trust updates)

### Migrations
All schema changes are version-controlled via Alembic. Current version: `9cbc11040b5c_initial_schema`

**Apply migrations:**
```bash
alembic upgrade head
```

**Create new migration:**
```bash
alembic revision --autogenerate -m "Description"
alembic upgrade head
```

---

## Configuration

### Environment Variables
```bash
# Database
DATABASE_URL=sqlite:///./test.db
DATABASE_URL_POSTGRES=postgresql+asyncpg://user:pass@localhost/hustle

# ML Models
ML_MODELS_DIR=app/ml/models

# Feature flags
ENABLE_RANKING_TRACE=true
ENABLE_MATCH_DEBUG=false

# Security
JWT_SECRET_KEY=your-secret-key
JWT_ALGORITHM=HS256

# API
API_PREFIX=/api/v1
```

### Settings
All configuration is centralized in `app/core/config.py` using Pydantic `BaseSettings`:

```python
from app.core.config import settings
print(settings.database_url)
print(settings.max_worker_search_radius)
```

---

## Testing

### Test Coverage
- **Unit tests** — Feature extraction, calibration, scoring
- **Integration tests** — Full match → accept → feedback flow
- **Endpoint tests** — API contract, schema validation, error handling
- **Stability tests** — Phase 2.6 observability layer backward compatibility

### Run Tests
```bash
# All tests
pytest tests/ -v

# Specific test file
pytest tests/test_integration.py -v

# With coverage
pytest tests/ --cov=app
```

### Known Issues & Missing Models
Missing ML models (normal for fresh setup):
- `app/ml/models/acceptance_model.joblib` — Predictor falls back to base rates
- `app/ml/models/risk_model.joblib` — Risk predictor falls back to 5% base rate
- `app/ml/models/acceptance_calibration.joblib` — Platt scaler uses raw probabilities
- `app/ml/models/risk_calibration.joblib` — Platt scaler uses raw probabilities

Tests with fallback expectations pass; tests expecting specific scores may show `WARNING` logs.

---

## Development Workflow

### Add a new endpoint
1. Create route handler in `api/v1/endpoints/`
2. Define request/response schemas in `schemas/`
3. Implement business logic in `services/`
4. Add tests to `tests/`
5. Update this README if needed

### Add a new database model
1. Create model in `db/models/`
2. Generate migration: `alembic revision --autogenerate -m "..."`
3. Review and apply: `alembic upgrade head`
4. Update schema here if needed

### Troubleshooting
- **Import errors** — Ensure `.venv` is activated
- **DB connection fails** — Check `DATABASE_URL` and Alembic migrations applied
- **Tests timeout** — Increase pytest timeout or check for hanging async operations
- **ML models missing** — Expected on fresh setup; use `train_acceptance_model.py` if available

---

## Roadmap

### Completed ✅
- [x] Core matching engine with rule-based + ML scoring
- [x] Risk prediction pipeline with calibration
- [x] Ranking trace and observability layer
- [x] Async DB session management
- [x] Feedback loop for trust updates
- [x] Basic analytics endpoint
- [x] Health probes and liveness checks

### In Progress 🔄
- [ ] Fix remaining 16 test failures (ML model loading, endpoint routing)
- [ ] Add missing endpoint routes (analytics, webhook)
- [ ] Implement typed enum for match status

### Backlog 📋
- [ ] Worker profile consistency checks
- [ ] Rate limiting middleware
- [ ] Extended analytics (trends, top workers)
- [ ] End-to-end HTTP test flows
- [ ] Production deployment guide

---

## Support

For issues, questions, or contributions:
1. Check test output: `pytest tests/ -v --tb=short`
2. Review logs: `tail -f app.log`
3. Check config: `app/core/config.py`
4. See detailed notes in our version 1 docs: `PHASE_2.5_NOTES.md`, `PHASE_2_6_IMPLEMENTATION.md`

---

**Last Updated:** May 15, 2026 | **Phase:** 2.6 (Observability)
