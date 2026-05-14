from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, desc
from pydantic import BaseModel
from app.db.session import get_db
from app.dependencies import get_current_user
from app.models.user import User
from app.db.models.wallet import (EmployerWallet, WorkerWallet, WalletTransaction, Withdrawal)
from app.services.squad_service import SquadService
from app.services.escrow_service import EscrowService

router = APIRouter(prefix="/wallet", tags=["wallet"])


# ── Employer: Initiate top-up via Dynamic VA ───────────────────────

class TopUpRequest(BaseModel):
    amount_kobo: int
    duration:    int = 600  # seconds — default 10 minutes


@router.post("/topup/initiate")
async def initiate_topup(
    body:         TopUpRequest,
    current_user: User = Depends(get_current_user),
    db:           AsyncSession = Depends(get_db),
):
    if current_user.role != "employer":
        raise HTTPException(status_code=403, detail="Employers only")

    if body.amount_kobo < 100000:
        raise HTTPException(
            status_code=400,
            detail="Minimum top-up is ₦1,000"
        )

    reference = SquadService.generate_ref("HUSTLE_TOPUP")

    result = await SquadService.initiate_dynamic_va(
        amount_kobo     = body.amount_kobo,
        transaction_ref = reference,
        email           = current_user.email or "",
        duration        = body.duration,
    )

    data = result["data"]

    return {
        "reference":              reference,
        "virtual_account_number": data["virtual_account_number"],
        "bank_name":              data.get("bank_name", "GTBank"),
        "account_name":           data.get("account_name", "Hustle Platform"),
        "amount_kobo":            body.amount_kobo,
        "expires_in_seconds":     body.duration,
    }


# ── Employer: Re-query top-up status ──────────────────────────────

@router.get("/topup/status/{reference}")
async def check_topup_status(
    reference:    str,
    current_user: User = Depends(get_current_user),
):
    result = await SquadService.requery_dynamic_va(reference)
    attempts = result.get("data", [])

    # Find latest successful attempt
    success = next(
        (a for a in attempts if a["transaction_status"] == "SUCCESS"),
        None,
    )

    if success:
        return {
            "status":      "success",
            "amount_kobo": int(float(success["amount_received"]) * 100),
            "reference":   reference,
        }

    # Check if any attempt exists
    if attempts:
        latest = attempts[-1]
        return {
            "status":    latest["transaction_status"].lower(),
            "reference": reference,
        }

    return {"status": "pending", "reference": reference}


# ── Wallet balance ─────────────────────────────────────────────────

@router.get("/balance")
async def get_balance(
    current_user: User = Depends(get_current_user),
    db:           AsyncSession = Depends(get_db),
):
    if current_user.role == "employer":
        result = await db.execute(
            select(EmployerWallet).where(
                EmployerWallet.user_id == str(current_user.id)
            )
        )
        wallet = result.scalar_one_or_none()
        return {
            "available_kobo": wallet.available_kobo if wallet else 0,
            "locked_kobo":    wallet.locked_kobo    if wallet else 0,
            "total_spent":    wallet.total_spent     if wallet else 0,
            "this_month":     0,  # compute separately if needed
        }

    result = await db.execute(
        select(WorkerWallet).where(
            WorkerWallet.user_id == str(current_user.id)
        )
    )
    wallet = result.scalar_one_or_none()
    return {
        "available_kobo":  wallet.available_kobo  if wallet else 0,
        "total_earned":    wallet.total_earned     if wallet else 0,
        "total_withdrawn": wallet.total_withdrawn  if wallet else 0,
        "this_month":      0,
    }


# ── Transaction history ────────────────────────────────────────────

@router.get("/transactions")
async def get_transactions(
    current_user: User = Depends(get_current_user),
    db:           AsyncSession = Depends(get_db),
    limit:        int = 20,
):
    result = await db.execute(
        select(WalletTransaction)
        .where(WalletTransaction.user_id == str(current_user.id))
        .order_by(desc(WalletTransaction.created_at))
        .limit(limit)
    )
    txns = result.scalars().all()
    return {
        "data": [
            {
                "id":            str(t.id),
                "type":          t.type,
                "amount_kobo":   t.amount_kobo,
                "balance_after": t.balance_after,
                "description":   t.description,
                "reference":     t.reference,
                "status":        t.status,
                "created_at":    t.created_at.isoformat(),
            }
            for t in txns
        ]
    }


# ── Worker: Account lookup ─────────────────────────────────────────

class LookupRequest(BaseModel):
    bank_code:      str
    account_number: str


@router.post("/lookup")
async def lookup_account(
    body:         LookupRequest,
    current_user: User = Depends(get_current_user),
):
    if current_user.role != "worker":
        raise HTTPException(status_code=403, detail="Workers only")

    result = await SquadService.lookup_account(
        bank_code      = body.bank_code,
        account_number = body.account_number,
    )
    return {
        "account_name":   result["data"]["account_name"],
        "account_number": body.account_number,
        "bank_code":      body.bank_code,
    }


# ── Worker: Withdraw ───────────────────────────────────────────────

class WithdrawRequest(BaseModel):
    amount_kobo:    int
    bank_code:      str
    account_number: str
    account_name:   str


@router.post("/withdraw")
async def withdraw(
    body:         WithdrawRequest,
    current_user: User = Depends(get_current_user),
    db:           AsyncSession = Depends(get_db),
):
    if current_user.role != "worker":
        raise HTTPException(status_code=403, detail="Workers only")

    result = await EscrowService.initiate_withdrawal(
        db             = db,
        worker_id      = str(current_user.id),
        amount_kobo    = body.amount_kobo,
        bank_code      = body.bank_code,
        account_number = body.account_number,
        account_name   = body.account_name,
    )
    return result