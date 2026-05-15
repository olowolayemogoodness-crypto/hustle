import uuid
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from pydantic import BaseModel
from app.db.session import get_db
from app.db.models.user import User
from app.models.wallet import EscrowRecord
from app.services.escrow_service import EscrowService, calculate_employer_charge
from app.dependencies import require_employer, get_current_user

router = APIRouter(prefix="/escrow", tags=["escrow"])


class EscrowLockRequest(BaseModel):
    job_id:         str
    worker_id:      str
    job_value_kobo: int


@router.post("/lock")
async def lock_escrow(
    body:         EscrowLockRequest,
    current_user: User = Depends(require_employer),
    db:           AsyncSession = Depends(get_db),
):
    total, worker_amount, fee = calculate_employer_charge(body.job_value_kobo)
    try:
        escrow = await EscrowService.lock_funds(
            db             = db,
            job_id         = body.job_id,
            employer_id    = str(current_user.id),
            worker_id      = body.worker_id,
            job_value_kobo = body.job_value_kobo,
        )
        return {
            "escrow_id":         str(escrow.id),
            "job_id":            body.job_id,
            "total_charged":     total,
            "worker_receives":   worker_amount,
            "platform_fee":      fee,
            "status":            escrow.status,
        }
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


class EscrowReleaseRequest(BaseModel):
    job_id: str


@router.post("/release")
async def release_escrow(
    body:         EscrowReleaseRequest,
    current_user: User = Depends(require_employer),
    db:           AsyncSession = Depends(get_db),
):
    try:
        escrow = await EscrowService.release_escrow(
            db          = db,
            job_id      = body.job_id,
            employer_id = str(current_user.id),
        )
        return {
            "message":         "Escrow released. Worker has been paid.",
            "job_id":          body.job_id,
            "worker_paid":     escrow.worker_amount_kobo,
            "platform_fee":    escrow.platform_fee_kobo,
            "status":          escrow.status,
        }
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/{job_id}")
async def get_escrow_status(
    job_id:       str,
    current_user: User = Depends(get_current_user),
    db:           AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(EscrowRecord).where(EscrowRecord.job_id == job_id)
    )
    escrow = result.scalar_one_or_none()
    if not escrow:
        raise HTTPException(status_code=404, detail="Escrow not found")

    return {
        "escrow_id":           str(escrow.id),
        "job_id":              escrow.job_id,
        "status":              escrow.status,
        "total_kobo":          escrow.total_kobo,
        "worker_amount_kobo":  escrow.worker_amount_kobo,
        "platform_fee_kobo":   escrow.platform_fee_kobo,
    }
