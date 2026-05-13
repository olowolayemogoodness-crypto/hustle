"""Example: Using the repository layer with UnitOfWork.

This example shows how to use the repository pattern and unit of work
for proper transaction management in the Hustle backend.
"""

# Example 1: Simple query with repository
# ==========================================

from fastapi import Depends
from app.db.repos_deps import get_unit_of_work
from app.db.repositories import UnitOfWork

@router.get("/api/v1/jobs/{job_id}/matches")
async def get_job_matches(
    job_id: str,
    uow: UnitOfWork = Depends(get_unit_of_work),
):
    """Get all matches for a job using repository pattern."""
    try:
        parsed_job_id = parse_uuid(job_id)
        
        # Use repository to query
        matches = await uow.match_logs.get_by_job_id(parsed_job_id)
        
        # Data is already fetched, transaction will auto-commit on context exit
        return {"job_id": job_id, "matches": len(matches)}
    except Exception as e:
        logger.error("Failed to get matches: %s", e)
        raise HTTPException(status_code=500, detail="Database error")


# Example 2: Multi-step transaction with rollback
# ================================================

@router.post("/api/v1/match/accept-batch")
async def accept_multiple_matches(
    payload: AcceptBatchRequest,
    uow: UnitOfWork = Depends(get_unit_of_work),
):
    """Accept multiple matches in a single transaction.
    
    If any match fails to accept, all changes are rolled back.
    """
    async with uow:  # Automatic commit on success, rollback on error
        try:
            accepted_count = 0
            for job_id, worker_id in payload.matches:
                # Query
                match_log = await uow.match_logs.get_by_job_and_worker(job_id, worker_id)
                if match_log:
                    # Update
                    await uow.match_logs.update(
                        match_log.id,
                        accepted=True,
                        status="selected"
                    )
                    accepted_count += 1
            
            # Explicit commit is not needed with async context manager
            # It automatically commits if no exception is raised
            
            return {"accepted": accepted_count}
            
        except Exception as e:
            logger.error("Batch accept failed: %s", e)
            # UnitOfWork context manager will auto-rollback on exception
            raise HTTPException(status_code=500, detail="Transaction failed")


# Example 3: Complex workflow with multiple repositories
# =======================================================

@router.post("/api/v1/match")
async def create_match_with_validation(
    payload: MatchRequest,
    uow: UnitOfWork = Depends(get_unit_of_work),
):
    """Create match while validating job and worker exist."""
    async with uow:
        # 1. Validate job exists
        job = await uow.jobs.get_by_id(payload.job_id)
        if not job:
            raise HTTPException(status_code=404, detail="Job not found")
        
        # 2. Validate worker exists
        worker = await uow.worker_profiles.get_by_user_id(payload.worker_id)
        if not worker:
            raise HTTPException(status_code=404, detail="Worker not found")
        
        # 3. Create match log
        match_log = await uow.match_logs.create(
            job_id=job.id,
            worker_id=worker.user_id,
            final_score=payload.score,
            rule_score=payload.rule_score,
            ml_probability=payload.ml_probability,
            risk_penalty=payload.risk_penalty,
            confidence=payload.confidence,
            status="ranked",
        )
        
        # 4. All changes committed together or none at all
        return {"match_log_id": str(match_log.id)}


# Key Benefits of Repository Pattern
# ===================================

"""
1. SEPARATION OF CONCERNS
   - Business logic separated from database queries
   - Repositories handle all data access
   
2. TRANSACTION MANAGEMENT
   - UnitOfWork ensures atomic operations
   - Automatic rollback on errors
   - Explicit flush/commit control
   
3. TESTABILITY
   - Mock repositories for unit tests
   - No need for database in tests
   
4. MAINTAINABILITY
   - All queries for a model in one place
   - Consistent error handling
   - Easy to add caching/optimization
   
5. CONSISTENCY
   - Type-safe queries
   - Structured CRUD operations
   - Reduced code duplication


Repository Methods Available
=============================

BaseRepository (inherited by all):
  - create(**kwargs) -> T
  - get_by_id(id) -> Optional[T]
  - list_all(limit, offset) -> List[T]
  - update(id, **kwargs) -> Optional[T]
  - delete(id) -> bool
  - exists(**kwargs) -> bool

MatchLogRepository (in addition):
  - get_by_job_id(job_id) -> List[MatchLog]
  - get_by_worker_id(worker_id) -> List[MatchLog]
  - get_by_job_and_worker(job_id, worker_id) -> Optional[MatchLog]
  - get_accepted_matches(job_id) -> List[MatchLog]
  - get_top_matches(job_id, limit) -> List[MatchLog]

JobRepository (in addition):
  - get_by_title(title) -> Optional[Job]
  - get_by_employer(employer_id) -> List[Job]

WorkerProfileRepository (in addition):
  - get_by_user_id(user_id) -> Optional[WorkerProfile]
  - get_verified_workers() -> List[WorkerProfile]


Transaction Patterns
====================

Pattern 1: Fire-and-forget (auto-commit)
  async with uow:
      await uow.match_logs.create(...)
      # Auto-commits on exit

Pattern 2: Conditional operations
  async with uow:
      match = await uow.match_logs.get_by_id(id)
      if match:
          await uow.match_logs.delete(id)

Pattern 3: Manual flush (peek before commit)
  async with uow:
      log = await uow.match_logs.create(...)
      await uow.flush()  # Makes it visible to queries within transaction
      other_logs = await uow.match_logs.get_by_job_id(log.job_id)

Pattern 4: Rollback on error
  async with uow:
      try:
          await uow.match_logs.create(...)
          # Error here auto-rollbacks
      except Exception:
          pass  # Changes discarded
"""
