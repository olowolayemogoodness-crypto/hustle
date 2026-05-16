from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.session import get_db
from app.schemas.auth import (
    OTPSendRequest, OTPVerifyRequest,
    TokenResponse, RoleSetRequest, KYCSubmitRequest,
)
from app.services import auth_service, kyc_service
from app.dependencies import get_current_user, require_worker, require_employer
from app.db.models.user import User

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/otp/send")
async def send_otp(
    body: OTPSendRequest,
    db: AsyncSession = Depends(get_db),
):
    result = await auth_service.send_otp(body.phone, db)
    return result


@router.post("/otp/verify", response_model=TokenResponse)
async def verify_otp(
    body: OTPVerifyRequest,
    db: AsyncSession = Depends(get_db),
):
    try:
        return await auth_service.verify_otp(body.phone, body.otp, db)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.post("/role")
async def set_role(
    body: RoleSetRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Set worker or employer role — called once after first login."""
    if current_user.role is not None and current_user.role != body.role:
        raise HTTPException(
        status_code=status.HTTP_400_BAD_REQUEST,
        detail=f"Role already set to {current_user.role}",
    )
    current_user.role = body.role
    db.add(current_user)

    # Create the matching profile row
    if body.role == "worker":
        from app.db.models.worker_profile import WorkerProfile
        profile = WorkerProfile(user_id=current_user.id)
        db.add(profile)
    else:
        from app.db.models.employer_profile import EmployerProfile
        profile = EmployerProfile(user_id=current_user.id)
        db.add(profile)

    await db.commit()
    return {"message": f"Role set to {body.role}"}


@router.post("/kyc/submit")
async def submit_kyc(
    body: KYCSubmitRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Submit NIN for KYC verification."""
    try:
        result = await kyc_service.submit_nin(current_user, body.nin, db)
        return result
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.get("/me")
async def get_me(current_user: User = Depends(get_current_user)):
    return {
        "id": str(current_user.id),
        "phone": current_user.phone,
        "full_name": current_user.full_name,
        "role": current_user.role,
        "kyc_status": current_user.kyc_status,
        "avatar_url": current_user.avatar_url,
    }