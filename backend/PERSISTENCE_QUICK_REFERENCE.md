# Quick Reference: Using the Persistence Layer

## Fast Start

### 1. Inject UnitOfWork into your endpoint

```python
from fastapi import APIRouter, Depends
from app.db.repos_deps import get_unit_of_work
from app.db.repositories import UnitOfWork

@router.post("/matches")
async def create_match(
    payload: MatchPayload,
    uow: UnitOfWork = Depends(get_unit_of_work),
):
    async with uow:
        # Your code here
        return result
```

### 2. Query data

```python
# Single query
match = await uow.match_logs.get_by_id(match_id)

# Multiple queries
matches = await uow.match_logs.get_by_job_id(job_id)

# Filtered queries
top_matches = await uow.match_logs.get_top_matches(job_id, limit=10)
```

### 3. Create/Update/Delete

```python
async with uow:
    # Create
    log = await uow.match_logs.create(
        job_id=job_id,
        worker_id=worker_id,
        final_score=0.95,
        status="ranked"
    )
    
    # Update
    await uow.match_logs.update(log.id, accepted=True)
    
    # Delete
    await uow.match_logs.delete(log.id)
    
    # Auto-commits on successful exit
```

## Common Patterns

### Pattern 1: Simple Query

```python
@router.get("/jobs/{job_id}/match-count")
async def count_job_matches(job_id: str, uow: UnitOfWork = Depends(get_unit_of_work)):
    async with uow:
        matches = await uow.match_logs.get_by_job_id(job_id)
        return {"count": len(matches)}
```

### Pattern 2: Create and Return

```python
@router.post("/matches")
async def create_match(payload: MatchPayload, uow: UnitOfWork = Depends(get_unit_of_work)):
    async with uow:
        match = await uow.match_logs.create(
            job_id=payload.job_id,
            worker_id=payload.worker_id,
            final_score=payload.score,
            status="ranked"
        )
        return {"id": str(match.id)}
```

### Pattern 3: Conditional Operations

```python
@router.post("/matches/{match_id}/accept")
async def accept_match(match_id: str, uow: UnitOfWork = Depends(get_unit_of_work)):
    async with uow:
        match = await uow.match_logs.get_by_id(match_id)
        
        if not match:
            raise HTTPException(status_code=404)
        
        if match.accepted:
            raise HTTPException(status_code=409, detail="Already accepted")
        
        await uow.match_logs.update(match_id, accepted=True, status="selected")
        return {"accepted": True}
```

### Pattern 4: Multi-Repository Transaction

```python
@router.post("/bulk-accept")
async def bulk_accept(payload: BulkAcceptRequest, uow: UnitOfWork = Depends(get_unit_of_work)):
    async with uow:
        results = {"accepted": 0, "rejected": 0}
        
        for job_id, worker_id in payload.matches:
            # Validate job exists
            job = await uow.jobs.get_by_id(job_id)
            if not job:
                results["rejected"] += 1
                continue
            
            # Validate worker exists
            worker = await uow.worker_profiles.get_by_user_id(worker_id)
            if not worker:
                results["rejected"] += 1
                continue
            
            # Update match
            match = await uow.match_logs.get_by_job_and_worker(job_id, worker_id)
            if match:
                await uow.match_logs.update(match.id, accepted=True)
                results["accepted"] += 1
        
        # Auto-commits all changes together
        return results
```

### Pattern 5: Flush and Inspect

```python
@router.post("/matches/validate")
async def validate_matches(job_id: str, uow: UnitOfWork = Depends(get_unit_of_work)):
    async with uow:
        # Create initial match
        match = await uow.match_logs.create(
            job_id=job_id,
            worker_id=worker_id,
            final_score=0.5,
            status="ranked"
        )
        
        # Flush to make it visible for queries
        await uow.flush()
        
        # Query the match we just created
        all_matches = await uow.match_logs.get_by_job_id(job_id)
        
        if len(all_matches) > 100:
            # Rollback if something looks wrong
            await uow.rollback()
            raise HTTPException(status_code=400, detail="Too many matches")
        
        # Otherwise commit on exit
```

## Available Repositories

### MatchLogRepository

```python
await uow.match_logs.get_by_id(id)
await uow.match_logs.get_by_job_id(job_id)
await uow.match_logs.get_by_worker_id(worker_id)
await uow.match_logs.get_by_job_and_worker(job_id, worker_id)
await uow.match_logs.get_accepted_matches(job_id)
await uow.match_logs.get_top_matches(job_id, limit=10)

# CRUD
await uow.match_logs.create(**kwargs)
await uow.match_logs.update(id, **kwargs)
await uow.match_logs.delete(id)
await uow.match_logs.list_all(limit=100, offset=0)
await uow.match_logs.exists(**kwargs)
```

### JobRepository

```python
await uow.jobs.get_by_id(id)
await uow.jobs.get_by_title(title)
await uow.jobs.get_by_employer(employer_id)

# CRUD
await uow.jobs.create(**kwargs)
await uow.jobs.update(id, **kwargs)
await uow.jobs.delete(id)
await uow.jobs.list_all(limit=100, offset=0)
await uow.jobs.exists(**kwargs)
```

### WorkerProfileRepository

```python
await uow.worker_profiles.get_by_id(id)
await uow.worker_profiles.get_by_user_id(user_id)
await uow.worker_profiles.get_verified_workers()

# CRUD
await uow.worker_profiles.create(**kwargs)
await uow.worker_profiles.update(id, **kwargs)
await uow.worker_profiles.delete(id)
await uow.worker_profiles.list_all(limit=100, offset=0)
await uow.worker_profiles.exists(**kwargs)
```

## Transaction Behavior

### Auto-Commit (Recommended)
```python
async with uow:
    result = await uow.match_logs.create(...)
    # Commits automatically on exit
```

### Auto-Rollback on Error
```python
async with uow:
    result = await uow.match_logs.create(...)
    # If exception raised here, auto-rollbacks
    risky_operation()
```

### Manual Flush
```python
async with uow:
    result = await uow.match_logs.create(...)
    await uow.flush()  # Makes visible to queries
    matches = await uow.match_logs.get_by_job_id(...)
```

### Manual Commit/Rollback
```python
uow = UnitOfWork(session)
try:
    result = await uow.match_logs.create(...)
    await uow.commit()
except Exception:
    await uow.rollback()
finally:
    await uow.close()
```

## Error Handling

```python
@router.post("/matches")
async def create(payload: MatchPayload, uow: UnitOfWork = Depends(get_unit_of_work)):
    try:
        async with uow:
            match = await uow.match_logs.create(
                job_id=payload.job_id,
                worker_id=payload.worker_id,
                final_score=payload.score,
                status="ranked"
            )
            return {"id": str(match.id)}
    except IntegrityError:
        # Constraint violation (duplicate, foreign key, etc.)
        raise HTTPException(status_code=400, detail="Invalid data")
    except SQLAlchemyError as e:
        # Database error
        logger.error("Database error: %s", e)
        raise HTTPException(status_code=500, detail="Database error")
```

## Adding Custom Queries

Add methods to repository classes:

```python
# In app/db/repositories/match_log.py

class MatchLogRepository(BaseRepository[MatchLog]):
    # ... existing code ...
    
    async def get_completed_matches(self, job_id: UUID) -> List[MatchLog]:
        """Get all completed matches for a job."""
        stmt = select(MatchLog).where(
            (MatchLog.job_id == job_id) & 
            (MatchLog.completed == True)
        )
        result = await self.session.execute(stmt)
        return result.scalars().all()
    
    async def get_disputed_matches(self) -> List[MatchLog]:
        """Get all matches with disputes."""
        stmt = select(MatchLog).where(MatchLog.dispute_occurred == True)
        result = await self.session.execute(stmt)
        return result.scalars().all()
```

Then use in endpoints:

```python
async with uow:
    completed = await uow.match_logs.get_completed_matches(job_id)
    disputed = await uow.match_logs.get_disputed_matches()
```

## Database Migrations

### Generate migrations

```bash
# Auto-generate from model changes
alembic revision --autogenerate -m "Add new field"

# View generated migration
cat migrations/versions/<id>_add_new_field.py
```

### Apply migrations

```bash
# Upgrade database
alembic upgrade head

# Downgrade
alembic downgrade -1

# Check current version
alembic current
```

## Testing with Repositories

```python
import pytest
from unittest.mock import AsyncMock, MagicMock

class MockMatchLogRepository:
    async def get_by_job_id(self, job_id):
        return []
    
    async def create(self, **kwargs):
        return MagicMock(id="test-id")

# In test
def test_endpoint(client):
    # No database needed
    # Mock repositories as needed
    pass
```
