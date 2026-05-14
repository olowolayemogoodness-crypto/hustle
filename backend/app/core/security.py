from functools import lru_cache
import jwt
from jwt import PyJWKClient
from fastapi import HTTPException, status
from app.core.config import settings


@lru_cache(maxsize=1)
def _get_jwks_client() -> PyJWKClient:
    url = f"{settings.supabase_url}/auth/v1/.well-known/jwks.json"
    print(f"JWKS URL: {url}")  # debug
    return PyJWKClient(url, cache_keys=True)


def decode_access_token(token: str) -> dict:
    try:
        client = _get_jwks_client()
        signing_key = client.get_signing_key_from_jwt(token)

        unverified = jwt.decode(token, options={"verify_signature": False})
        print("Unverified payload:", unverified)
        print("Signing key:", signing_key.key)

        return jwt.decode(
            token,
            signing_key.key,
            algorithms=["ES256"],
            audience="authenticated",
        )
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token has expired")
    except jwt.InvalidTokenError as e:
        print("JWT error:", e)
        raise HTTPException(status_code=401, detail=f"Invalid token: {e}")