# app/dependencies.py
import jwt
import httpx
import json
from jwt.algorithms import ECAlgorithm
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.session import get_db
from app.db.models.user import User
from app.core.config import settings
from app.services.auth_service import get_or_create_user
import logging

logger = logging.getLogger(__name__)
bearer_scheme = HTTPBearer()

SUPABASE_JWKS_URL = f"{settings.supabase_url}/auth/v1/.well-known/jwks.json"

# Cache the public key — fetch once, reuse forever
_public_key = None


def _get_public_key_sync() -> object:
    """Fetch and cache Supabase public key synchronously at startup."""
    import httpx as _httpx
    global _public_key
    if _public_key is not None:
        return _public_key
    resp  = _httpx.get(SUPABASE_JWKS_URL)
    jwks  = resp.json()
    key   = jwks["keys"][0]
    _public_key = ECAlgorithm.from_jwk(json.dumps(key))
    logger.info("Supabase public key cached")
    return _public_key


# Pre-fetch on import
try:
    _get_public_key_sync()
except Exception as e:
    logger.warning(f"Could not pre-fetch JWKS: {e}")


def _decode_supabase_token(token: str) -> dict:
    try:
        public_key = _get_public_key_sync()
        payload = jwt.decode(
            token,
            public_key,
            algorithms=["ES256"],
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
    payload    = _decode_supabase_token(credentials.credentials)
    user_id    = payload.get("sub")
    email      = payload.get("email", "")
    full_name  = payload.get("user_metadata", {}).get("full_name")
    avatar_url = payload.get("user_metadata", {}).get("avatar_url")

    if not user_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token payload",
        )

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