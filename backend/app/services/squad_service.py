import hashlib
import hmac
import uuid
from datetime import datetime
import httpx
from app.core.env import Env

class SquadService:

    @staticmethod
    def _headers() -> dict:
        return {
            "Authorization": f"Bearer {Env.squad_secret_key}",
            "Content-Type":  "application/json",
        }

    # ── Virtual Account ────────────────────────────────────────────

    @staticmethod
    async def create_virtual_account(
        user_id:     str,
        first_name:  str,
        last_name:   str,
        email:       str,
        phone:       str,
        bvn:         str,
        dob:         str,       # MM/DD/YYYY
        gender:      str,       # "1" = Male, "2" = Female
        address:     str,
        beneficiary_account: str,  # your GTBank account
    ) -> dict:
        customer_identifier = f"HUSTLE_{user_id[:8].upper()}"

        async with httpx.AsyncClient() as client:
            resp = await client.post(
                f"{Env.squad_base_url}/virtual-account",
                headers=SquadService._headers(),
                json={
                    "customer_identifier":  customer_identifier,
                    "first_name":           first_name,
                    "last_name":            last_name,
                    "mobile_num":           phone,
                    "email":                email,
                    "bvn":                  bvn,
                    "dob":                  dob,
                    "address":              address,
                    "gender":               gender,
                    "beneficiary_account":  beneficiary_account,
                },
                timeout=30,
            )
            resp.raise_for_status()
            return resp.json()

    # ── Account Lookup ─────────────────────────────────────────────

    @staticmethod
    async def lookup_account(
        bank_code:      str,
        account_number: str,
    ) -> dict:
        async with httpx.AsyncClient() as client:
            resp = await client.post(
                f"{Env.squad_base_url}/payout/account/lookup",
                headers=SquadService._headers(),
                json={
                    "bank_code":      bank_code,
                    "account_number": account_number,
                },
                timeout=15,
            )
            resp.raise_for_status()
            return resp.json()

    # ── Transfer (Worker Withdrawal) ───────────────────────────────

    @staticmethod
    async def transfer_to_bank(
        amount_kobo:    int,
        bank_code:      str,
        account_number: str,
        account_name:   str,
        narration:      str,
        reference:      str,
    ) -> dict:
        async with httpx.AsyncClient() as client:
            resp = await client.post(
                f"{Env.squad_base_url}/payout/transfer",
                headers=SquadService._headers(),
                json={
                    "transaction_reference": reference,
                    "amount":                amount_kobo,
                    "bank_code":             bank_code,
                    "account_number":        account_number,
                    "account_name":          account_name,
                    "currency":              "NGN",
                    "narration":             narration,
                },
                timeout=30,
            )
            resp.raise_for_status()
            return resp.json()

    # ── Ledger Balance ─────────────────────────────────────────────

    @staticmethod
    async def get_ledger_balance() -> dict:
        async with httpx.AsyncClient() as client:
            resp = await client.get(
                f"{Env.squad_base_url}/merchant/balance",
                headers=SquadService._headers(),
                timeout=15,
            )
            resp.raise_for_status()
            return resp.json()

    # ── Webhook Signature Validation ───────────────────────────────

    @staticmethod
    def verify_webhook(
        payload_body: bytes,
        signature:    str,
    ) -> bool:
        """
        Validates x-squad-encrypted-body header.
        HMAC-SHA512 of raw body using secret key.
        """
        expected = hmac.new(
            Env.squad_secret_key.encode(),
            payload_body,
            hashlib.sha512,
        ).hexdigest().upper()
        return hmac.compare_digest(expected, signature.upper())

    # ── Generate unique transaction reference ──────────────────────

    @staticmethod
    def generate_ref(prefix: str = "HUSTLE") -> str:
        return f"{prefix}_{uuid.uuid4().hex[:16].upper()}"