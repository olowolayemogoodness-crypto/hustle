import random
import string
from datetime import datetime, timedelta, timezone
import httpx
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update
from app.core.config import settings
from app.models.user import User
from app.models.otp import OTPCode
from app.core.security import create_access_token
from app.schemas.auth import TokenResponse, UserInToken
import logging

logger = logging.getLogger(__name__)

OTP_EXPIRE_MINUTES = 5
MAX_OTP_ATTEMPTS = 3


def _generate_otp() -> str:
    return "".join(random.choices(string.digits, k=6))


async def send_otp(phone: str, db: AsyncSession) -> dict:
    """
    Generate OTP, store it, send via Termii.
    For dev/test: returns OTP in response (remove in prod).
    """
    code = _generate_otp()
    expires_at = datetime.now(timezone.utc) + timedelta(minutes=OTP_EXPIRE_MINUTES)

    # Invalidate any existing unused OTPs for this phone
    await db.execute(
        update(OTPCode)
        .where(OTPCode.phone == phone, OTPCode.used == False)
        .values(used=True)
    )

    otp_record = OTPCode(
        phone=phone,
        code=code,
        expires_at=expires_at,
    )
    db.add(otp_record)
    await db.commit()

    # Send via Termii
    sent = await _send_via_termii(phone, code)

    response = {
        "message": "OTP sent",
        "expires_in": OTP_EXPIRE_MINUTES * 60,
    }
    # Only expose OTP in dev — remove before prod
    if settings.debug:
        response["otp_debug"] = code

    return response


async def verify_otp(phone: str, otp: str, db: AsyncSession) -> TokenResponse:
    """
    Verify OTP → upsert user → return JWT.
    """
    # Fetch latest valid OTP for this phone
    result = await db.execute(
        select(OTPCode)
        .where(
            OTPCode.phone == phone,
            OTPCode.used == False,
            OTPCode.expires_at > datetime.now(timezone.utc),
        )
        .order_by(OTPCode.created_at.desc())
        .limit(1)
    )
    otp_record = result.scalar_one_or_none()

    if not otp_record:
        raise ValueError("OTP expired or not found. Request a new one.")

    # Increment attempt counter
    otp_record.attempts += 1
    if otp_record.attempts >= MAX_OTP_ATTEMPTS:
        otp_record.used = True
        await db.commit()
        raise ValueError("Too many incorrect attempts. Request a new OTP.")

    if otp_record.code != otp:
        await db.commit()
        raise ValueError(f"Incorrect OTP. {MAX_OTP_ATTEMPTS - otp_record.attempts} attempt(s) left.")

    # Mark OTP used
    otp_record.used = True
    await db.commit()

    # Upsert user
    result = await db.execute(select(User).where(User.phone == phone))
    user = result.scalar_one_or_none()
    is_new = user is None

    if is_new:
        user = User(phone=phone)
        db.add(user)
        await db.commit()
        await db.refresh(user)

    # Create JWT
    token = create_access_token({
        "sub": str(user.id),
        "phone": user.phone,
        "role": user.role,
        "kyc_status": user.kyc_status,
    })

    return TokenResponse(
        access_token=token,
        expires_in=settings.jwt_expire_minutes * 60,
        user=UserInToken(
            id=str(user.id),
            phone=user.phone,
            role=user.role,
            kyc_status=user.kyc_status,
            is_new_user=is_new,
        ),
    )


async def _send_via_termii(phone: str, code: str) -> bool:
    """Send OTP SMS via Termii (Nigerian SMS gateway)."""
    try:
        async with httpx.AsyncClient(timeout=10) as client:
            resp = await client.post(
                "https://api.ng.termii.com/api/sms/send",
                json={
                    "to": phone,
                    "from": settings.termii_sender_id,
                    "sms": f"Your LocGig verification code is {code}. Valid for {OTP_EXPIRE_MINUTES} minutes. Do not share this.",
                    "type": "plain",
                    "channel": "dnd",
                    "api_key": settings.termii_api_key,
                },
            )
            return resp.status_code == 200
    except Exception as e:
        logger.error(f"Termii SMS failed for {phone}: {e}")
        return False