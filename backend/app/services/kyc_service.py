from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.models.user import User
from app.models.worker_profile import WorkerProfile
from app.models.kyc_submission import KYCSubmission
from app.ml.trust_calculator import calculate_trust_score


async def submit_nin(user: User, nin: str, db: AsyncSession) -> dict:
    """
    MVP: Store NIN and mark as verified immediately.
    Phase 2: Integrate NIBSS / Prembly NIN verification API.
    """
    if user.kyc_status == "verified":
        raise ValueError("NIN already verified")

    # Check NIN not already used by another account
    result = await db.execute(select(User).where(User.nin == nin))
    existing = result.scalar_one_or_none()
    if existing and existing.id != user.id:
        raise ValueError("This NIN is linked to another account")

    # Store submission log
    submission = KYCSubmission(user_id=user.id, nin=nin, status="verified")
    db.add(submission)

    # Update user record
    user.nin = nin
    user.kyc_status = "verified"

    # If worker — recalculate trust score with verification bonus
    if user.role == "worker":
        result = await db.execute(
            select(WorkerProfile).where(WorkerProfile.user_id == user.id)
        )
        profile = result.scalar_one_or_none()
        if profile:
            profile.is_verified = True
            new_score = calculate_trust_score(
                completion_rate=profile.completion_rate,
                avg_rating=profile.avg_rating,
                total_jobs=profile.total_jobs,
                disputes_count=profile.disputes_count,
                is_verified=True,
            )
            profile.trust_score = new_score
            db.add(profile)

    await db.commit()
    return {
        "message": "NIN verified successfully",
        "kyc_status": "verified",
        "trust_score_updated": user.role == "worker",
    }