import uuid
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from pydantic import BaseModel
from app.db.session import get_db
from app.db.models.user import User
from app.db.models.worker_profile import WorkerProfile
from app.db.models.employer_profile import EmployerProfile
from app.dependencies import get_current_user

router = APIRouter(prefix="/profile", tags=["profile"])


# ── Worker ────────────────────────────────────────────────────────

class WorkerProfileUpdate(BaseModel):
    skills:           list[str] | None = None
    experience_level: str | None = None
    job_radius_km:    int | None = None
    availability:     str | None = None
    bio:              str | None = None
    is_available:     bool | None = None


def _worker_to_dict(profile: WorkerProfile) -> dict:
    return {
        "id":               str(profile.id),
        "user_id":          str(profile.user_id),
        "skills":           profile.skills or [],
        "experience_level": profile.experience_level,
        "job_radius_km":    profile.job_radius_km,
        "availability":     profile.availability,
        "bio":              profile.bio,
        "trust_score":      profile.trust_score,
        "completion_rate":  profile.completion_rate,
        "avg_rating":       profile.avg_rating,
        "total_jobs":       profile.total_jobs,
        "is_verified":      profile.is_verified,
        "is_available":     profile.is_available,
    }


@router.get("/worker")
async def get_my_worker_profile(
    current_user: User = Depends(get_current_user),
    db:           AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(WorkerProfile).where(WorkerProfile.user_id == current_user.id)
    )
    profile = result.scalar_one_or_none()
    if not profile:
        raise HTTPException(status_code=404, detail="Worker profile not found")
    return _worker_to_dict(profile)


@router.put("/worker")
async def update_worker_profile(
    body:         WorkerProfileUpdate,
    current_user: User = Depends(get_current_user),
    db:           AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(WorkerProfile).where(WorkerProfile.user_id == current_user.id)
    )
    profile = result.scalar_one_or_none()
    if not profile:
        raise HTTPException(status_code=404, detail="Worker profile not found")

    if body.skills           is not None: profile.skills           = body.skills
    if body.experience_level is not None: profile.experience_level = body.experience_level
    if body.job_radius_km    is not None: profile.job_radius_km    = body.job_radius_km
    if body.availability     is not None: profile.availability     = body.availability
    if body.bio              is not None: profile.bio              = body.bio
    if body.is_available     is not None: profile.is_available     = body.is_available

    db.add(profile)
    await db.commit()
    await db.refresh(profile)
    return _worker_to_dict(profile)


@router.get("/worker/{user_id}")
async def get_worker_profile_by_id(
    user_id:      str,
    current_user: User = Depends(get_current_user),
    db:           AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(WorkerProfile).where(
            WorkerProfile.user_id == uuid.UUID(user_id)
        )
    )
    profile = result.scalar_one_or_none()
    if not profile:
        raise HTTPException(status_code=404, detail="Worker profile not found")
    return _worker_to_dict(profile)


# ── Employer ──────────────────────────────────────────────────────

class EmployerProfileUpdate(BaseModel):
    company_name: str | None = None
    industry:     str | None = None
    description:  str | None = None


def _employer_to_dict(profile: EmployerProfile) -> dict:
    return {
        "id":               str(profile.id),
        "user_id":          str(profile.user_id),
        "company_name":     profile.company_name,
        "industry":         profile.industry,
        "rating":           profile.rating,
        "total_jobs_posted": profile.total_jobs_posted,
        "verified":         profile.verified,
        "description":      profile.description,
    }


@router.get("/employer")
async def get_my_employer_profile(
    current_user: User = Depends(get_current_user),
    db:           AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(EmployerProfile).where(
            EmployerProfile.user_id == current_user.id
        )
    )
    profile = result.scalar_one_or_none()
    if not profile:
        raise HTTPException(status_code=404, detail="Employer profile not found")
    return _employer_to_dict(profile)


@router.put("/employer")
async def update_employer_profile(
    body:         EmployerProfileUpdate,
    current_user: User = Depends(get_current_user),
    db:           AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(EmployerProfile).where(
            EmployerProfile.user_id == current_user.id
        )
    )
    profile = result.scalar_one_or_none()
    if not profile:
        raise HTTPException(status_code=404, detail="Employer profile not found")

    if body.company_name is not None: profile.company_name = body.company_name
    if body.industry     is not None: profile.industry     = body.industry
    if body.description  is not None: profile.description  = body.description

    db.add(profile)
    await db.commit()
    await db.refresh(profile)
    return _employer_to_dict(profile)
