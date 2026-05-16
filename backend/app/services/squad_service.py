import hashlib
import hmac
import uuid
import httpx
from app.core.config import settings


class SquadService:

    @staticmethod
    def _headers() -> dict:
        return {
            "Authorization": f"Bearer {settings.squad_secret_key}",
            "Content-Type":  "application/json",
        }

    @staticmethod
    def generate_ref(prefix: str = "HUSTLE") -> str:
        return f"{prefix}_{uuid.uuid4().hex[:16].upper()}"

    # ── Static Virtual Account ─────────────────────────────────────

    @staticmethod
    async def create_static_va(
        customer_identifier: str,
        first_name:          str,
        last_name:           str,
        email:               str,
        phone:               str,
        bvn:                 str,
        dob:                 str,
        gender:              str,
        address:             str,
        beneficiary_account: str,
    ) -> dict:
        """Create a permanent virtual account for an employer."""
        async with httpx.AsyncClient() as client:
            resp = await client.post(
                f"{settings.squad_base_url}/virtual-account",
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
            if not resp.is_success:
                raise Exception(f"Squad error: {resp.status_code} - {resp.text}")
            return resp.json()

    @staticmethod
    async def get_static_va(customer_identifier: str) -> dict:
        """Get VA details by customer identifier."""
        async with httpx.AsyncClient() as client:
            resp = await client.get(
                f"{settings.squad_base_url}/virtual-account/{customer_identifier}",
                headers=SquadService._headers(),
                timeout=15,
            )
            if not resp.is_success:
                raise Exception(f"Squad error: {resp.status_code} - {resp.text}")
            return resp.json()

    @staticmethod
    async def simulate_payment(
    virtual_account_number: str,
    amount:                 int,
) -> dict:
        async with httpx.AsyncClient() as client:
            resp = await client.post(
            f"{settings.squad_base_url}/virtual-account/simulate/payment",
            headers=SquadService._headers(),
            json={
                "virtual_account_number": virtual_account_number,
                "amount":                 str(amount),  # ← string not int
            },
            timeout=15,
        )
        if not resp.is_success:
            raise Exception(f"Squad error: {resp.status_code} - {resp.text}")
        return resp.json()
    # ── Transfer API ───────────────────────────────────────────────

    @staticmethod
    async def lookup_account(
        bank_code:      str,
        account_number: str,
    ) -> dict:
        """Verify recipient bank account before transfer."""
        async with httpx.AsyncClient() as client:
            resp = await client.post(
                f"{settings.squad_base_url}/payout/account/lookup",
                headers=SquadService._headers(),
                json={
                    "bank_code":      bank_code,
                    "account_number": account_number,
                },
                timeout=15,
            )
            if not resp.is_success:
                raise Exception(f"Squad error: {resp.status_code} - {resp.text}")
            return resp.json()

    @staticmethod
    async def transfer_to_bank(
        amount_kobo:    int,
        bank_code:      str,
        account_number: str,
        account_name:   str,
        narration:      str,
        reference:      str,
    ) -> dict:
        """Send funds from Squad ledger to any Nigerian bank."""
        async with httpx.AsyncClient() as client:
            resp = await client.post(
                f"{settings.squad_base_url}/payout/transfer",
                headers=SquadService._headers(),
                json={
                    "transaction_reference": reference,
                    "amount":                str(amount_kobo),
                    "bank_code":             bank_code,
                    "account_number":        account_number,
                    "account_name":          account_name,
                    "currency_id":           "NGN",
                    "remark":                narration,
                },
                timeout=30,
            )
            if not resp.is_success:
                raise Exception(f"Squad error: {resp.status_code} - {resp.text}")
            return resp.json()

    @staticmethod
    async def requery_transfer(transaction_ref: str) -> dict:
        """Re-query transfer status — call on 424 timeout."""
        async with httpx.AsyncClient() as client:
            resp = await client.post(
                f"{settings.squad_base_url}/payout/requery",
                headers=SquadService._headers(),
                json={"transaction_reference": transaction_ref},
                timeout=15,
            )
            if not resp.is_success:
                raise Exception(f"Squad error: {resp.status_code} - {resp.text}")
            return resp.json()

    # ── Webhook validation ─────────────────────────────────────────

    @staticmethod
    def verify_webhook(body: bytes, signature: str) -> bool:
        """Validate x-squad-encrypted-body header."""
        computed = hmac.new(
            settings.squad_secret_key.encode(),
            body,
            hashlib.sha512,
        ).hexdigest()
        return hmac.compare_digest(computed, signature.lower())
