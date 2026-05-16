from fastapi import APIRouter, Request, Header
from sqlalchemy import select, cast, String
from app.db.session import get_db
from app.db.models.user import User
from app.services.squad_service import SquadService
from app.services.escrow_service import EscrowService
import logging

router = APIRouter(prefix="/webhook", tags=["webhook"])
logger = logging.getLogger(__name__)


@router.post("/squad")
async def squad_webhook(
    request:                Request,
    x_squad_encrypted_body: str = Header(None),
):
    body    = await request.body()
    payload = await request.json()

    logger.info(f"Squad webhook received: {payload}")

    # Skip signature for sandbox testing
    # Re-enable in production:
    # if not SquadService.verify_webhook(body, x_squad_encrypted_body):
    #     raise HTTPException(status_code=401, detail="Invalid signature")

    transaction_indicator = payload.get("transaction_indicator")
    customer_identifier   = payload.get("customer_identifier", "")
    principal_amount      = payload.get("principal_amount", "0")
    transaction_ref       = payload.get("transaction_reference", "")

    # Only process credits
    if transaction_indicator != "C":
        logger.info(f"Skipping non-credit: {transaction_indicator}")
        return {"response_code": 200, "response_description": "Noted"}

    amount_kobo = int(float(principal_amount) * 100)
    if amount_kobo <= 0:
        return {"response_code": 200, "response_description": "Invalid amount"}

    # Extract user ID prefix from customer_identifier
    # Format: HUSTLE_89ABB3F8 → first 8 chars of user UUID
    identifier_part = customer_identifier.replace("HUSTLE_", "").lower()
    logger.info(f"Looking up user with prefix: {identifier_part}")

    async for db in get_db():
        # Find user by UUID prefix
        result = await db.execute(
            select(User).where(
                cast(User.id, String).ilike(f"{identifier_part}%")
            )
        )
        user = result.scalar_one_or_none()

        if not user:
            logger.error(f"No user found for: {customer_identifier}")
            return {
                "response_code":        200,
                "response_description": "User not found",
            }

        logger.info(f"Found user: {user.id} ({user.email})")

        await EscrowService.credit_employer_wallet(
            db          = db,
            user_id     = str(user.id),
            amount_kobo = amount_kobo,
            squad_ref   = transaction_ref,
        )
        break

    logger.info(f"✅ Wallet credited ₦{amount_kobo/100:.2f} → {customer_identifier}")

    return {
        "response_code":         200,
        "transaction_reference": transaction_ref,
        "response_description":  "Success",
    }
