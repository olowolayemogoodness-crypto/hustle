from datetime import datetime, timedelta, timezone
from typing import Any
import jwt
from fastapi import HTTPException, status
from app.core.config import settings
from jwt import PyJWKClient
ALGORITHM = "HS256"


def create_access_token(payload: dict[str, Any]) -> str:
    """
    Create a signed JWT.
    payload must include 'sub' (user UUID) and 'phone'.
    """
    expire = datetime.now(timezone.utc) + timedelta(
        minutes=settings.jwt_expire_minutes
    )
    data = {
        **payload,
        "exp": expire,
        "iat": datetime.now(timezone.utc),
    }
    return jwt.encode(data, settings.jwt_secret, algorithm=ALGORITHM)


_jwks_client = PyJWKClient(f"{settings.supabase_url}/auth/v1/.well-known/jwks.json")


def decode_access_token(token: str) -> dict:
    try:
        signing_key = _jwks_client.get_signing_key_from_jwt(token)
        payload = jwt.decode(
            token,
            signing_key.key,
            algorithms=["ES256"],
            audience="authenticated",
        )
        return payload
    except jwt.ExpiredSignatureError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token has expired",
        )
    except jwt.InvalidTokenError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token",
        )
