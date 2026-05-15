import uuid
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, desc
from pydantic import BaseModel
from app.db.session import get_db
from app.db.models.application import Application
from app.db.models.job import Job
from app.db.models.user import User
from app.dependencies import get_current_user, require_worker, require_employer

router = APIRouter(prefix="/applications", tags=["applications"])


class ApplicationCreate(BaseModel):
    job_id:        str
    cover_letter:  str | None = None
    proposed_rate: float | None = None


def _app_to_dict(app: Application) -> dict:
    return {
        "id":            str(app.id),
        "job_id":        str(app.job_id),
        "worker_id":     str(app.worker_id),
        "cover_letter":  app.cover_letter,
        "proposed_rate": app.proposed_rate,
        "is_accepted":   app.is_accepted,
        "status":        "accepted" if app.is_accepted else "pending",
        "created_at":    app.created_at.isoformat() if app.created_at else None,
    }


@router.post("")
async def apply_for_job(
    body:         ApplicationCreate,
    current_user: User = Depends(require_worker),
    db:           AsyncSession = Depends(get_db),
):
    # Check job exists
    result = await db.execute(
        select(Job).where(Job.id == uuid.UUID(body.job_id))
    )
    job = result.scalar_one_or_none()
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")

    # Check not already applied
    existing = await db.execute(
        select(Application).where(
            Application.job_id   == uuid.UUID(body.job_id),
            Application.worker_id == current_user.id,
        )
    )
    if existing.scalar_one_or_none():
        raise HTTPException(status_code=400, detail="Already applied for this job")

    app = Application(
        job_id        = uuid.UUID(body.job_id),
        worker_id     = current_user.id,
        cover_letter  = body.cover_letter,
        proposed_rate = body.proposed_rate,
        is_accepted   = False,
    )
    db.add(app)
    await db.commit()
    await db.refresh(app)
    return _app_to_dict(app)


@router.get("/my")
async def get_my_applications(
    current_user: User = Depends(require_worker),
    db:           AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(Application)
        .where(Application.worker_id == current_user.id)
        .order_by(desc(Application.created_at))
    )
    apps = result.scalars().all()
    return {"data": [_app_to_dict(a) for a in apps]}


@router.get("/job/{job_id}")
async def get_job_applications(
    job_id:       str,
    current_user: User = Depends(require_employer),
    db:           AsyncSession = Depends(get_db),
):
    # Verify job belongs to employer
    result = await db.execute(
        select(Job).where(
            Job.id          == uuid.UUID(job_id),
            Job.employer_id == current_user.id,
        )
    )
    if not result.scalar_one_or_none():
        raise HTTPException(status_code=404, detail="Job not found")

    result = await db.execute(
        select(Application)
        .where(Application.job_id == uuid.UUID(job_id))
        .order_by(desc(Application.created_at))
    )
    apps = result.scalars().all()
    return {"data": [_app_to_dict(a) for a in apps]}


@router.post("/{application_id}/accept")
async def accept_application(
    application_id: str,
    current_user:   User = Depends(require_employer),
    db:             AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(Application).where(
            Application.id == uuid.UUID(application_id)
        )
    )
    app = result.scalar_one_or_none()
    if not app:
        raise HTTPException(status_code=404, detail="Application not found")

    # Verify the job belongs to this employer
    job_result = await db.execute(
        select(Job).where(
            Job.id          == app.job_id,
            Job.employer_id == current_user.id,
        )
    )
    if not job_result.scalar_one_or_none():
        raise HTTPException(status_code=403, detail="Not your job")

    app.is_accepted = True
    db.add(app)
    await db.commit()
    return {"message": "Application accepted", "application_id": application_id}


@router.post("/{application_id}/reject")
async def reject_application(
    application_id: str,
    current_user:   User = Depends(require_employer),
    db:             AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(Application).where(
            Application.id == uuid.UUID(application_id)
        )
    )
    app = result.scalar_one_or_none()
    if not app:
        raise HTTPException(status_code=404, detail="Application not found")

    job_result = await db.execute(
        select(Job).where(
            Job.id          == app.job_id,
            Job.employer_id == current_user.id,
        )
    )
    if not job_result.scalar_one_or_none():
        raise HTTPException(status_code=403, detail="Not your job")

    app.is_accepted = False
    db.add(app)
    await db.commit()
    return {"message": "Application rejected", "application_id": application_id}
