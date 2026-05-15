import math
import uuid
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, desc
from pydantic import BaseModel
from app.db.session import get_db
from app.db.models.job import Job
from app.db.models.application import Application
from app.db.models.user import User
from app.dependencies import get_current_user, require_employer, require_worker

router = APIRouter(prefix="/jobs", tags=["jobs"])


# ── Schemas ───────────────────────────────────────────────────────

class JobCreate(BaseModel):
    title:          str
    description:    str | None = None
    required_skills: list[str] = []
    latitude:       float
    longitude:      float
    location_name:  str | None = None
    pay_per_worker: int          # kobo
    workers_needed: int = 1
    budget:         float | None = None
    urgency:        int = 1


class JobResponse(BaseModel):
    id:              str
    employer_id:     str
    title:           str
    description:     str | None
    required_skills: list
    latitude:        float | None
    longitude:       float | None
    location_name:   str | None
    pay_per_worker:  int
    workers_needed:  int
    workers_hired:   int
    status:          str
    budget:          float | None
    urgency:         int | None
    distance_km:     float | None = None
    created_at:      str


def _job_to_dict(job: Job, distance_km: float | None = None) -> dict:
    return {
        "id":              str(job.id),
        "employer_id":     str(job.employer_id),
        "title":           job.title,
        "description":     job.description,
        "required_skills": job.required_skills or [],
        "latitude":        job.latitude,
        "longitude":       job.longitude,
        "location_name":   getattr(job, 'location_name', None),
        "pay_per_worker":  getattr(job, 'pay_per_worker', 0),
        "workers_needed":  getattr(job, 'workers_needed', 1),
        "workers_hired":   getattr(job, 'workers_hired', 0),
        "status":          getattr(job, 'status', 'open'),
        "budget":          job.budget,
        "urgency":         job.urgency,
        "distance_km":     round(distance_km, 2) if distance_km else None,
        "created_at":      job.created_at.isoformat() if job.created_at else None,
    }


def _haversine(lat1: float, lng1: float, lat2: float, lng2: float) -> float:
    """Distance in km between two coordinates."""
    R = 6371
    dlat = math.radians(lat2 - lat1)
    dlng = math.radians(lng2 - lng1)
    a = (math.sin(dlat / 2) ** 2 +
         math.cos(math.radians(lat1)) *
         math.cos(math.radians(lat2)) *
         math.sin(dlng / 2) ** 2)
    return R * 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))


# ── Endpoints ─────────────────────────────────────────────────────

@router.post("")
async def create_job(
    body:         JobCreate,
    current_user: User = Depends(require_employer),
    db:           AsyncSession = Depends(get_db),
):
    job = Job(
        employer_id     = current_user.id,
        title           = body.title,
        description     = body.description,
        required_skills = body.required_skills,
        latitude        = body.latitude,
        longitude       = body.longitude,
        budget          = body.budget,
        urgency         = body.urgency,
    )
    # Set extra fields if they exist on model
    if hasattr(job, 'location_name'):  job.location_name  = body.location_name
    if hasattr(job, 'pay_per_worker'): job.pay_per_worker = body.pay_per_worker
    if hasattr(job, 'workers_needed'): job.workers_needed = body.workers_needed
    if hasattr(job, 'status'):         job.status         = "open"

    db.add(job)
    await db.commit()
    await db.refresh(job)
    return _job_to_dict(job)


@router.get("/nearby")
async def get_nearby_jobs(
    lat:          float = Query(..., description="Worker latitude"),
    lng:          float = Query(..., description="Worker longitude"),
    radius_km:    float = Query(default=5.0),
    skill:        str | None = Query(default=None),
    limit:        int = Query(default=20),
    current_user: User = Depends(get_current_user),
    db:           AsyncSession = Depends(get_db),
):
    # Bounding box approximation
    lat_delta = radius_km / 111.0
    lng_delta = radius_km / (111.0 * math.cos(math.radians(lat)))

    query = select(Job).where(
        Job.latitude.between(lat - lat_delta, lat + lat_delta),
        Job.longitude.between(lng - lng_delta, lng + lng_delta),
    )

    result = await db.execute(query)
    jobs = result.scalars().all()

    # Calculate exact distance + filter
    nearby = []
    for job in jobs:
        if job.latitude is None or job.longitude is None:
            continue
        dist = _haversine(lat, lng, job.latitude, job.longitude)
        if dist <= radius_km:
            nearby.append((job, dist))

    # Sort by distance
    nearby.sort(key=lambda x: x[1])

    return {
        "data": [_job_to_dict(job, dist) for job, dist in nearby[:limit]]
    }


@router.get("/my-posts")
async def get_my_posts(
    current_user: User = Depends(require_employer),
    db:           AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(Job)
        .where(Job.employer_id == current_user.id)
        .order_by(desc(Job.created_at))
    )
    jobs = result.scalars().all()
    return {"data": [_job_to_dict(j) for j in jobs]}


@router.get("/{job_id}")
async def get_job(
    job_id:       str,
    current_user: User = Depends(get_current_user),
    db:           AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(Job).where(Job.id == uuid.UUID(job_id))
    )
    job = result.scalar_one_or_none()
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    return _job_to_dict(job)


@router.post("/{job_id}/complete")
async def complete_job(
    job_id:       str,
    current_user: User = Depends(require_employer),
    db:           AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(Job).where(
            Job.id == uuid.UUID(job_id),
            Job.employer_id == current_user.id,
        )
    )
    job = result.scalar_one_or_none()
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")

    if hasattr(job, 'status'):
        job.status = "completed"

    db.add(job)
    await db.commit()
    return {"message": "Job marked as complete", "job_id": job_id}


@router.post("/{job_id}/cancel")
async def cancel_job(
    job_id:       str,
    current_user: User = Depends(require_employer),
    db:           AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(Job).where(
            Job.id == uuid.UUID(job_id),
            Job.employer_id == current_user.id,
        )
    )
    job = result.scalar_one_or_none()
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")

    if hasattr(job, 'status'):
        job.status = "cancelled"

    db.add(job)
    await db.commit()
    return {"message": "Job cancelled", "job_id": job_id}
