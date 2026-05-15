import jwt
import httpx
from cryptography.hazmat.primitives.asymmetric.ec import EllipticCurvePublicKey
from jwt.algorithms import ECAlgorithm
import json
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
async def _get_public_key(token: str):
    header = jwt.get_unverified_header(token)
    token_kid = header.get("kid")
    print(f"Token kid: {token_kid}")

    async with httpx.AsyncClient() as client:
        resp = await client.get(SUPABASE_JWKS_URL)
        jwks = resp.json()

    print(f"Available kids: {[k['kid'] for k in jwks['keys']]}")

    key_data = next(
        (k for k in jwks["keys"] if k["kid"] == token_kid),
        None
    )

    if key_data is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="No matching signing key found",
        )

    return ECAlgorithm.from_jwk(json.dumps(key_data))


async def _decode_supabase_token(token: str) -> dict:
    try:
        public_key = await _get_public_key(token)
        payload = jwt.decode(
            token,
            public_key,
            algorithms=["ES256"],
            audience="authenticated",
        )
        return payload
    except HTTPException:
        raise
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
    payload = await _decode_supabase_token(credentials.credentials)

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
