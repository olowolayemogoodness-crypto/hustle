import hashlib
import hmac
import uuid
import httpx
from app.core.env import Env


class SquadService:

    @staticmethod
    def _headers() -> dict:
        return {
            "Authorization": f"Bearer {Env.squad_secret_key}",
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
                f"{Env.squad_base_url}/virtual-account/initiate-dynamic-virtual-account",
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
                f"{Env.squad_base_url}/virtual-account/get-dynamic-virtual-account-transactions/{transaction_ref}",
                headers=SquadService._headers(),
                timeout=15,
            )
            resp.raise_for_status