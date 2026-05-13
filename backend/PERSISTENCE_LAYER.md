# Persistence Layer Architecture

## Overview

The Hustle backend implements a complete persistence layer with:
- **Alembic** - Database schema versioning
- **Repository Pattern** - Data access abstraction
- **Unit of Work** - Transaction management
- **Type Safety** - Generic repositories with full type hints

## Architecture Layers

```
┌─────────────────────────────────────┐
│     FastAPI Endpoints               │  Request/Response
├─────────────────────────────────────┤
│     Services (Business Logic)       │  Domain logic
├─────────────────────────────────────┤
│     Repository Layer (Data Access)  │  Repositories + UnitOfWork
├─────────────────────────────────────┤
│     SQLAlchemy ORM Models           │  Database mapping
├─────────────────────────────────────┤
│     Alembic Migrations              │  Schema versioning
├─────────────────────────────────────┤
│     Database (SQLite/PostgreSQL)    │  Persistence
└─────────────────────────────────────┘
```

## Repository Pattern

### What is a Repository?

A Repository encapsulates data access logic. Instead of spreading database queries throughout your code:

**Without Repository (anti-pattern):**
```python
@router.get("/matches/{job_id}")
async def get_matches(job_id: str, db: AsyncSession = Depends(get_db)):
    stmt = select(MatchLog).where(MatchLog.job_id == job_id)
    result = await db.execute(stmt)
    return result.scalars().all()
```

**With Repository (clean):**
```python
@router.get("/matches/{job_id}")
async def get_matches(job_id: str, uow: UnitOfWork = Depends(get_unit_of_work)):
    async with uow:
        return await uow.match_logs.get_by_job_id(job_id)
```

### Available Repositories

#### BaseRepository (inherited by all)
Generic CRUD operations available to all models:

```python
# Create
match_log = await uow.match_logs.create(
    job_id=job_id,
    worker_id=worker_id,
    final_score=0.95,
    status="ranked"
)

# Read
match_log = await uow.match_logs.get_by_id(match_log_id)

# List
all_logs = await uow.match_logs.list_all(limit=100, offset=0)

# Update
updated = await uow.match_logs.update(
    match_log_id,
    status="selected",
    accepted=True
)

# Delete
deleted = await uow.match_logs.delete(match_log_id)

# Check existence
exists = await uow.match_logs.exists(job_id=job_id, worker_id=worker_id)
```

#### MatchLogRepository
Specialized queries for match logs:

```python
# Get all matches for a job
matches = await uow.match_logs.get_by_job_id(job_id)

# Get all matches by a worker
worker_matches = await uow.match_logs.get_by_worker_id(worker_id)

# Get specific match
match = await uow.match_logs.get_by_job_and_worker(job_id, worker_id)

# Get accepted matches
accepted = await uow.match_logs.get_accepted_matches(job_id)

# Get top-scored matches
top_matches = await uow.match_logs.get_top_matches(job_id, limit=10)
```

#### JobRepository
Job-specific queries:

```python
# Get job by title
job = await uow.jobs.get_by_title("Delivery Job")

# Get all jobs by employer
employer_jobs = await uow.jobs.get_by_employer(employer_id)
```

#### WorkerProfileRepository
Worker profile queries:

```python
# Get worker profile by user
profile = await uow.worker_profiles.get_by_user_id(user_id)

# Get all verified workers
verified = await uow.worker_profiles.get_verified_workers()
```

## Unit of Work Pattern

The UnitOfWork class coordinates repositories and manages transactions:

### Single Repository Operations

```python
@router.post("/api/v1/match/accept")
async def accept_match(
    job_id: str,
    worker_id: str,
    uow: UnitOfWork = Depends(get_unit_of_work),
):
    async with uow:  # Transaction context
        match = await uow.match_logs.get_by_job_and_worker(job_id, worker_id)
        if not match:
            raise HTTPException(status_code=404)
        
        await uow.match_logs.update(
            match.id,
            accepted=True,
            status="selected"
        )
        # Auto-commits on context exit
        
        return {"accepted": True}
```

### Multi-Repository Transactions

```python
@router.post("/api/v1/match/accept-batch")
async def accept_batch(
    payload: AcceptBatchRequest,
    uow: UnitOfWork = Depends(get_unit_of_work),
):
    async with uow:  # All-or-nothing transaction
        accepted = []
        
        for job_id, worker_id in payload.matches:
            # Query job
            job = await uow.jobs.get_by_id(job_id)
            if not job:
                raise HTTPException(status_code=404)
            
            # Query worker
            worker = await uow.worker_profiles.get_by_user_id(worker_id)
            if not worker:
                raise HTTPException(status_code=404)
            
            # Create or update match
            match = await uow.match_logs.get_by_job_and_worker(job_id, worker_id)
            if match:
                await uow.match_logs.update(match.id, accepted=True)
                accepted.append(match.id)
        
        # All changes committed together or none at all
        return {"accepted": accepted}
```

### Transaction Control

```python
# Auto-commit (recommended)
async with uow:
    await uow.match_logs.create(...)
    # Commits automatically on successful exit

# Manual flush (inspect before commit)
async with uow:
    log = await uow.match_logs.create(...)
    await uow.flush()  # Make visible to queries
    
    other_logs = await uow.match_logs.get_by_job_id(log.job_id)
    if len(other_logs) > 10:
        await uow.rollback()
        raise Exception("Too many matches")

# Explicit control
uow = UnitOfWork(session)
try:
    await uow.match_logs.create(...)
    await uow.commit()
finally:
    await uow.close()
```

## Transaction Management

### Automatic Rollback on Error

```python
async with uow:
    result1 = await uow.match_logs.create(job_id=1, worker_id=1, score=0.9)
    
    # If this raises an exception
    result2 = await uow.match_logs.create(None, None, None)  # TypeError
    
    # Changes are automatically rolled back
    # Neither result1 nor result2 is persisted
```

### Savepoints (for nested transactions)

```python
async with uow:
    match = await uow.match_logs.create(...)
    await uow.flush()
    
    try:
        await risky_operation(uow)
    except Exception:
        await uow.rollback()
        # Try alternative
        await uow.match_logs.delete(match.id)
```

## Alembic Migrations

Alembic provides database schema versioning:

### Creating Migrations

```bash
# Auto-generate from model changes
alembic revision --autogenerate -m "Add rating to match_logs"

# View migration
cat migrations/versions/<id>_add_rating_to_match_logs.py
```

### Applying Migrations

```bash
# Upgrade to latest
alembic upgrade head

# Downgrade one version
alembic downgrade -1

# Check current version
alembic current
```

### Migration File Structure

```python
# migrations/versions/abc123_add_column.py

def upgrade() -> None:
    """Upgrade database schema."""
    op.add_column('match_logs', sa.Column('new_field', sa.String(), nullable=True))

def downgrade() -> None:
    """Downgrade database schema."""
    op.drop_column('match_logs', 'new_field')
```

## File Structure

```
backend/
├── app/
│   ├── db/
│   │   ├── repositories/
│   │   │   ├── __init__.py         # Repository exports
│   │   │   ├── base.py             # BaseRepository with generic CRUD
│   │   │   ├── match_log.py        # MatchLog-specific queries
│   │   │   ├── job.py              # Job-specific queries
│   │   │   ├── worker_profile.py   # WorkerProfile-specific queries
│   │   │   └── unit_of_work.py     # UnitOfWork transaction coordination
│   │   ├── repos_deps.py           # FastAPI dependency injection
│   │   ├── models/
│   │   ├── session.py              # Engine and session factory
│   │   └── init_db.py              # Database initialization
│   └── api/
│       └── match.py                # Endpoints using repositories
├── migrations/
│   ├── env.py                      # Alembic configuration
│   ├── script.py.mako              # Migration template
│   └── versions/
│       └── 9cbc11040b5c_initial_schema.py  # Initial migration
├── alembic.ini                     # Alembic settings
├── MIGRATIONS.md                   # Migration guide
├── PERSISTENCE_LAYER.md            # This file
└── REPOSITORY_EXAMPLES.md          # Code examples
```

## Design Benefits

### 1. Separation of Concerns
- Repositories handle data access
- Services handle business logic
- Endpoints handle HTTP concerns

### 2. Testability
```python
# Easy to mock in tests
class MockMatchLogRepository:
    async def get_by_job_id(self, job_id):
        return []  # Test data

# No database needed for unit tests
```

### 3. Consistency
- All database access goes through repositories
- Centralized error handling
- Consistent transaction boundaries

### 4. Maintainability
- Query location is obvious
- Easy to add caching, logging, metrics
- Single place to optimize database access

### 5. Flexibility
- Easy to add database layers (caching, sharding)
- Swap implementations without changing endpoints
- Type-safe queries across Python and database

## Next Steps

1. **Extend repositories** - Add more domain-specific queries
2. **Add caching** - Decorate repository methods with Redis caching
3. **Add migrations** - Run `alembic upgrade head` in CI/CD
4. **Update endpoints** - Migrate from raw SQLAlchemy to repositories
5. **Add validation** - Centralize business rule validation in repositories
