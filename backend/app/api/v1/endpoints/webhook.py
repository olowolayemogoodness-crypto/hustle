from fastapi import APIRouter, Request, HTTPException, Header
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.session import get_db
from app.services.squad_service import SquadService
from app.services.escrow_service import EscrowService
from app.core.config import settings
import logging

router = APIRouter(prefix="/webhook", tags=["webhook"])
logger = logging.getLogger(__name__)


@router.post("/squad")
async def squad_webhook(
    request: Request,
    x_squad_encrypted_body: str = Header(None),
):
    body = await request.body()

    # 1. Validate signature
    if not x_squad_encrypted_body:
        raise HTTPException(status_code=400, detail="Missing signature")

    if not SquadService.verify_webhook(body, x_squad_encrypted_body):
        logger.warning("Invalid Squad webhook signature")
        raise HTTPException(status_code=401, detail="Invalid signature")

    payload = await request.json()
    event   = payload.get("Event")

    logger.info(f"Squad webhook received: {event}")

    # 2. Only handle successful charges
    if event != "charge_successful":
        return {"status": "ignored"}

    body_data  = payload.get("Body", {})
    squad_ref  = body_data.get("transaction_ref")
    amount     = int(body_data.get("amount", 0))        # already in kobo
    email      = body_data.get("email", "")

    if not squad_ref or amount <= 0:
        raise HTTPException(status_code=400, detail="Invalid payload")

    # 3. Find employer by email
    result = supabase.from_("users") \
        .select("id") \
        .eq("email", email) \
        .maybe_single() \
        .execute()

    if not result.data:
        logger.error(f"No user found for email: {email}")
        return {"status": "user_not_found"}

    user_id = result.data["id"]

    # 4. Credit employer wallet (idempotent)
    async for db in get_db():
        await EscrowService.credit_employer_wallet(
            db          = db,
            user_id     = user_id,
            amount_kobo = amount,
            squad_ref   = squad_ref,
        )

    logger.info(f"Wallet credited: {user_id} ← ₦{amount/100:.2f}")

    # 5. Acknowledge to Squad (must return 200)
    return {
        "response_code":        200,
        "transaction_reference": squad_ref,
        "response_description":  "Success",
    }