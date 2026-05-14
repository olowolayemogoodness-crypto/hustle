from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.db.models.user import User
import logging

logger = logging.getLogger(__name__)


async def get_or_create_user(
    db:       AsyncSession,
    user_id:  str,
    email:    str,
    full_name: str | None = None,
    avatar_url: str | None = None,
) -> tuple[User, bool]:
    """
    Get existing user or create new one from Supabase auth data.
    Returns (user, is_new).
    """
    result = await db.execute(
        select(User).where(User.id == user_id)
    )
    user = result.scalar_one_or_none()

    if user:
        return user, False

    # New user — create record
    user = User(
        id         = user_id,
        email      = email,
        full_name  = full_name,
        avatar_url = avatar_url,
        kyc_status = "unverified",
    )
    db.add(user)
    await db.commit()
    await db.refresh(user)
    logger.info(f"New user created: {user_id} ({email})")
    return user, True


async def get_user_by_id(
    db:      AsyncSession,
    user_id: str,
) -> User | None:
    result = await db.execute(
        select(User).where(User.id == user_id)
    )
    return result.scalar_one_or_none()
