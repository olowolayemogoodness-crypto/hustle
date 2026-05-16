import uuid
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.db.models.user import User
import logging

logger = logging.getLogger(__name__)


async def get_or_create_user(
    db:         AsyncSession,
    user_id:    str,
    email:      str,
    full_name:  str,
    avatar_url: str | None = None,
) -> tuple[User, bool]:
    # 1. Try by ID first
    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()
    if user:
        return user, False

    # 2. Try by email (same person, different UUID)
    result = await db.execute(select(User).where(User.email == email))
    user = result.scalar_one_or_none()
    if user:
        return user, False

    # 3. Create new user
    try:
        user = User(
            id         = uuid.UUID(user_id),
            email      = email,
            full_name  = full_name,
            avatar_url = avatar_url,
            kyc_status = "unverified",
            is_active  = True,
        )
        db.add(user)
        await db.commit()
        await db.refresh(user)
        logger.info(f"Created user: {email}")
        return user, True

    except Exception as e:
        await db.rollback()
        # Race condition — fetch again
        result = await db.execute(select(User).where(User.email == email))
        user = result.scalar_one_or_none()
        if user:
            return user, False
        raise e


async def get_user_by_id(db: AsyncSession, user_id: str) -> User | None:
    result = await db.execute(
        select(User).where(User.id == uuid.UUID(user_id))
    )
    return result.scalar_one_or_none()
