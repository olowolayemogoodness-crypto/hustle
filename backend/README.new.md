# Hustle Backend — Version 1 MVP

## What this project is
Hustle Backend is the server-side engine for a job matching platform. It takes a job request, ranks available workers, and records match outcomes. It is built as a Minimum Viable Product (MVP) so it is fully functional while staying focused on the most important problem: matching jobs to workers safely and transparently.

This README is written for both technical and non-technical readers:
- if you are a judge or stakeholder, you can understand what the system does and why it matters
- if you are a developer, you can understand how it is structured and how to run it

---

## Why this matters
This backend helps employers find the best worker for a job, while also protecting the platform with risk scoring and feedback tracking.

In plain language:
- Employers post a job
- Workers are scored and ranked
- The platform recommends the best candidates
- Match decisions are stored and can be reviewed later
- User feedback helps the system improve over time

---

## What is included in this MVP
The core capabilities of version 1 are:
- job matching with ranked worker recommendations
- match acceptance and status updates
- match history retrieval
- simple feedback recording
- analytics summarizing match outcomes
- asynchronous database handling for reliable performance
- basic machine learning support for ranking and risk estimation

---

## Quick start

### Install and run
```bash
cd backend
python -m venv .venv
.venv\\Scripts\\activate
pip install -r requirements.txt
alembic upgrade head
python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### Run tests
```bash
cd backend
pytest tests/ -q
```

---

## How the backend works

### Simple explanation
1. The frontend or API client sends a job and candidate workers.
2. The backend ranks each worker using rules plus machine learning.
3. The highest-ranked workers are returned.
4. The accepted match is stored in the database.
5. The employer can update match status and submit feedback.

### Technical explanation
- **FastAPI** exposes REST endpoints for matching, accepting, status updates, and feedback.
- **SQLAlchemy** manages database models and async session management.
- **A lightweight ML pipeline** evaluates worker risk and acceptance likelihood.
- **Pydantic schemas** validate all requests and responses.
- **Alembic** tracks database schema changes.

---

## Core endpoints

### Match workers
- `POST /api/v1/match`
- Returns ranked workers and recommended worker IDs
- Uses a blend of rule-based scoring and ML probability

### Accept a match
- `POST /api/v1/match/accept`
- Marks a worker as accepted for a job

### Update match status
- `POST /api/v1/match/status`
- Tracks states like `viewed` and `selected`

### Get match history
- `GET /api/v1/match/history/{job_id}`
- Returns the recorded match events for a job

### Send feedback
- `POST /api/v1/feedback`
- Records completion, disputes, and ratings

### Health checks
- `GET /health/live`
- `GET /health/ready`

### Analytics
- `GET /api/v1/analytics/matches`
- Reports match volume, completion rate, and acceptance stats

---

## Architecture at a glance

### Main folders
- `app/api/v1/endpoints/` — API route handlers
- `app/services/` — Business logic for matching, logging, and feedback
- `app/ml/` — ML prediction and calibration code
- `app/db/` — Database models, sessions, and migrations
- `app/schemas/` — Request and response data validation
- `app/core/` — Configuration, logging, and middleware

### Database and data flow
- Matches are stored in `match_logs`
- Feedback updates worker and employer scores
- Models can use historical match records to improve ranking

---

## Project status
This is the **Hustle Backend MVP (Version 1)**.

What that means:
- the core matching experience works end to end
- the system is designed for real use, not just a prototype
- it is intentionally scoped to avoid unnecessary complexity
- it is ready for judges to review the concept and architecture

---

## Future roadmap

### Version 2 ideas
- add secure user authentication and access control
- save job postings and worker profiles permanently
- provide a dashboard for employers and workers
- improve the match recommendation experience
- add richer result explanations for trust and compliance

### Version 3 ideas
- deploy to cloud with monitoring, autoscaling, and a managed database
- support payments, escrow, and worker payouts
- add personalization and adaptive matching based on feedback
- enable real-time chat, notifications, and onboarding flows
- build a full marketplace with bidding and proposals

---

## Notes for non-technical readers
If you are not a developer, the important part is this:
- the backend is the part of the product that decides who should do a job
- it uses data to make smarter choices instead of choosing randomly
- it also records what happened so the team can improve the platform later
- we built the first version to show a complete matching process with growth potential

---

## Cleaner project structure
Temporary and generated files have been removed from this repository so the backend folder remains focused on source code, tests, migrations, and documentation.
