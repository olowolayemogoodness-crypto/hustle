import uuid
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, desc
from pydantic import BaseModel
from app.db.session import get_db
from app.dependencies import get_current_user
from app.db.models.user import User
from app.db.models.wallet import (
    EmployerWallet, WorkerWallet,
    WalletTransaction, Withdrawal,
)
from app.services.squad_service import SquadService
from app.services.escrow_service import EscrowService

router = APIRouter(prefix="/wallet", tags=["wallet"])


# ── Employer: Get/Create Static Virtual Account ────────────────────

class VACreateRequest(BaseModel):
    first_name:          str
    last_name:           str
    phone:               str
    bvn:                 str
    dob:                 str    # MM/DD/YYYY
    gender:              str    # "1" = Male, "2" = Female
    address:             str
    beneficiary_account: str    # GTBank account for settlement


@router.post("/virtual-account")
async def create_virtual_account(
    body:         VACreateRequest,
    current_user: User = Depends(get_current_user),
    db:           AsyncSession = Depends(get_db),
):
    """Create a permanent virtual account for employer top-ups."""
    if current_user.role != "employer":
        raise HTTPException(status_code=403, detail="Employers only")

    customer_identifier = f"HUSTLE_{str(current_user.id)[:8].upper()}"

    result = await SquadService.create_static_va(
        customer_identifier  = customer_identifier,
        first_name           = body.first_name,
        last_name            = body.last_name,
        email                = current_user.email or "",
        phone                = body.phone,
        bvn                  = body.bvn,
        dob                  = body.dob,
        gender               = body.gender,
        address              = body.address,
        beneficiary_account  = body.beneficiary_account,
    )

    data = result.get("data", {})
    return {
        "virtual_account_number": data.get("virtual_account_number"),
        "bank_name":              data.get("bank_name", "GTBank"),
        "customer_identifier":    customer_identifier,
        "message":                "Transfer any amount to this account to top up your wallet",
    }


@router.get("/virtual-account")
async def get_virtual_account(
    current_user: User = Depends(get_current_user),
):
    """Get employer's existing virtual account details."""
    if current_user.role != "employer":
        raise HTTPException(status_code=403, detail="Employers only")

    customer_identifier = f"HUSTLE_{str(current_user.id)[:8].upper()}"

    try:
        result = await SquadService.get_static_va(customer_identifier)
        data   = result.get("data", {})
        return {
            "virtual_account_number": data.get("virtual_account_number"),
            "bank_name":              data.get("bank_name", "GTBank"),
            "customer_identifier":    customer_identifier,
        }
    except Exception:
        raise HTTPException(
            status_code=404,
            detail="Virtual account not found. Create one first.",
        )


# ── Sandbox: Simulate payment ──────────────────────────────────────

class SimulateRequest(BaseModel):
    virtual_account_number: str
    amount:                 str  # kobo


@router.post("/simulate-payment")
async def simulate_payment(
    body:         SimulateRequest,
    current_user: User = Depends(get_current_user),
):
    """Sandbox only — simulate a payment to test webhook."""
    result = await SquadService.simulate_payment(
        virtual_account_number = body.virtual_account_number,
        amount                 = body.amount,
    )
    return result


# ── Wallet balance ─────────────────────────────────────────────────

@router.get("/balance")
async def get_balance(
    current_user: User = Depends(get_current_user),
    db:           AsyncSession = Depends(get_db),
):
    if current_user.role == "employer":
        result = await db.execute(
            select(EmployerWallet).where(
                EmployerWallet.user_id == current_user.id
            )
        )
        wallet = result.scalar_one_or_none()
        return {
            "available_kobo": wallet.available_kobo if wallet else 0,
            "locked_kobo":    wallet.locked_kobo    if wallet else 0,
            "total_spent":    wallet.total_spent     if wallet else 0,
            "this_month":     0,
        }

    result = await db.execute(
        select(WorkerWallet).where(
            WorkerWallet.user_id == current_user.id
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
        .where(WalletTransaction.user_id == current_user.id)
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
