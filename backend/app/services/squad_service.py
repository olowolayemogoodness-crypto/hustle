import hashlib
import hmac
import uuid
import httpx
from app.core.config import settings


class SquadService:
    @staticmethod
    async def initiate_payment(
        amount_kobo: int,
        transaction_ref: str,
        email: str,
    ) -> dict:
        async with httpx.AsyncClient() as client:
            resp = await client.post(
            f"{settings.squad_base_url}/transaction/initiate",
            headers=SquadService._headers(),
            json={
                "amount":          amount_kobo,
                "transaction_ref": transaction_ref,
                "email":           email,
                "currency":        "NGN",
                "initiate_type":   "inline",
            },
            timeout=30,
        )
        if not resp.is_success:
            print(f"Squad error: {resp.status_code} {resp.text}")
            resp.raise_for_status()
        return resp.json()



    @staticmethod
    async def verify_transaction(transaction_ref: str) -> dict:
        async with httpx.AsyncClient() as client:
            resp = await client.get(
            f"{settings.squad_base_url}/transaction/verify/{transaction_ref}",
            headers=SquadService._headers(),
            timeout=30,
        )
        if not resp.is_success:
            print(f"Squad verify error: {resp.status_code} {resp.text}")
            resp.raise_for_status()
        return resp.json()    
    @staticmethod
    def verify_webhook(body: bytes, signature: str) -> bool:
        computed = hmac.new(
        settings.squad_webhook_secret.encode(),
        body,
        hashlib.sha512,
    ).hexdigest()
        return hmac.compare_digest(computed, signature.lower())

    @staticmethod
    def _headers() -> dict:
        return {
            "Authorization": f"Bearer {settings.squad_secret_key}",
            "Content-Type":  "application/json",
        }

    # ── Generate unique reference ──────────────────────────────────
    @staticmethod
    def generate_ref(prefix: str = "HUSTLE") -> str:
        return f"{prefix}_{uuid.uuid4().hex[:16].upper()}"

    # ── Dynamic VA: Initiate transaction ──────────────────────────
    @staticmethod
    async def initiate_dynamic_va(
        amount_kobo:     int,
        transaction_ref: str,
        email:           str,
        duration:        int = 600,  # 10 minutes in seconds
    ) -> dict:
        """
        Assigns a VA from your pool for this transaction.
        Returns virtual_account_number, bank, expiry.
        """
        async with httpx.AsyncClient() as client:
            resp = await client.post(
                f"{settings.squad_base_url}/virtual-account/initiate-dynamic-virtual-account",
                headers=SquadService._headers(),
                json={
                    "amount":          amount_kobo,
                    "transaction_ref": transaction_ref,
                    "duration":        duration,
                    "email":           email,
                },
                timeout=30,
            )
            resp.raise_for_status()
            return resp.json()

    # ── Dynamic VA: Re-query transaction ──────────────────────────
    @staticmethod
    async def requery_dynamic_va(transaction_ref: str) -> dict:
        """
        Check all payment attempts for a transaction.
        Returns array of SUCCESS/MISMATCH/EXPIRED attempts.
        """
        async with httpx.AsyncClient() as client:
            resp = await client.get(
                f"{settings.squad_base_url}/virtual-account/get-dynamic-virtual-account-transactions/{transaction_ref}",
                headers=SquadService._headers(),
                timeout=15,
            )
            resp.raise_for_status