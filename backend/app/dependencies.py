import httpx
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.db.session import get_db
from app.db.models.user import User
from app.core.config import settings
from app.services.auth_service import get_or_create_user
import jwt
import logging

logger = logging.getLogger(__name__)
bearer_scheme = HTTPBearer()

# Supabase JWKS URL — used to verify ES256 tokens
SUPABASE_JWKS_URL = f"{settings.supabase_url}/auth/v1/.well-known/jwks.json"

_jwks_client = None

def _get_jwks_client():
    global _jwks_client
    if _jwks_client is None:
        _jwks_client = jwt.PyJWKClient(SUPABASE_JWKS_URL)
    return _jwks_client


def _decode_supabase_token(token: str) -> dict:
    """Verify and decode a Supabase JWT using their public key."""
    try:
        client   = _get_jwks_client()
        signing_key = client.get_signing_key_from_jwt(token)
        payload  = jwt.decode(
            token,
            signing_key.key,
            algorithms=["ES256", "RS256"],
            audience="authenticated",
        )
        return payload
    except jwt.ExpiredSignatureError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token expired",
        )
    except Exception as e:
        logger.warning(f"Token decode failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token",
        )


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(bearer_scheme),
    db:          AsyncSession = Depends(get_db),
) -> User:
    payload = _decode_supabase_token(credentials.credentials)

    user_id    = payload.get("sub")
    email      = payload.get("email", "")
    full_name  = payload.get("user_metadata", {}).get("full_name")
    avatar_url = payload.get("user_metadata", {}).get("avatar_url")

    if not user_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token payload",
        )

    # Get or create user in our DB
    user, _ = await get_or_create_user(
        db         = db,
        user_id    = user_id,
        email      = email,
        full_name  = full_name,
        avatar_url = avatar_url,
    )

    return user


async def require_worker(
    current_user: User = Depends(get_current_user),
) -> User:
    if current_user.role != "worker":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Worker access required",
        )
    return current_user


async def require_employer(
    current_user: User = Depends(get_current_user),
) -> User:
    if current_user.role != "employer":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Employer access required",
        )
    return current_user
