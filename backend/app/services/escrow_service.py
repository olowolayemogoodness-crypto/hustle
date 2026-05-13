from uuid import UUID
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update
from app.models import EscrowRecord, EmployerWallet, WorkerWallet, WalletTransaction
from app.core.env import Env
import logging

logger = logging.getLogger(__name__)

PLATFORM_FEE_PERCENT = Env.platform_fee_percent  # 2


def calculate_employer_charge(job_value_kobo: int) -> tuple[int, int, int]:
    """
    Returns (total_charge, worker_amount, platform_fee).

    Employer pays job value + 2% on top.
    Worker always receives 100% of job value.
    """
    platform_fee   = int(job_value_kobo * PLATFORM_FEE_PERCENT / 100)
    total_charge   = job_value_kobo + platform_fee
    worker_amount  = job_value_kobo
    return total_charge, worker_amount, platform_fee


class EscrowService:

    # ── Step 1: Employer tops up wallet via Squad VA ───────────────

    @staticmethod
    async def credit_employer_wallet(
        db:           AsyncSession,
        user_id:      str,
        amount_kobo:  int,
        squad_ref:    str,
    ) -> None:
        """Called from webhook when Squad confirms payment."""

        # Idempotency check — prevent double credit
        existing = await db.execute(
            select(WalletTransaction).where(
                WalletTransaction.reference == squad_ref
            )
        )
        if existing.scalar_one_or_none():
            logger.warning(f"Duplicate webhook ref: {squad_ref}")
            return

        # Credit employer wallet
        result = await db.execute(
            select(EmployerWallet).where(
                EmployerWallet.user_id == user_id
            )
        )
        wallet = result.scalar_one_or_none()
        if not wallet:
            wallet = EmployerWallet(user_id=user_id)
            db.add(wallet)

        wallet.available_kobo += amount_kobo

        # Log transaction
        tx = WalletTransaction(
            user_id      = user_id,
            type         = "topup",
            amount_kobo  = amount_kobo,
            balance_after = wallet.available_kobo,
            reference    = squad_ref,
            description  = "Wallet top-up via Squad",
        )
        db.add(tx)
        await db.commit()

    # ── Step 2: Employer posts job — lock funds in escrow ──────────

    @staticmethod
    async def lock_funds(
        db:           AsyncSession,
        job_id:       str,
        employer_id:  str,
        worker_id:    str,
        job_value_kobo: int,
    ) -> EscrowRecord:
        """
        Employer is charged job_value + 2%.
        Worker always receives full job_value.
        """

        total_charge, worker_amount, platform_fee = \
            calculate_employer_charge(job_value_kobo)

        # Check employer has enough balance for total (job + fee)
        result = await db.execute(
            select(EmployerWallet).where(
                EmployerWallet.user_id == employer_id
            )
        )
        wallet = result.scalar_one_or_none()
        if not wallet or wallet.available_kobo < total_charge:
            shortfall = total_charge - (wallet.available_kobo if wallet else 0)
            raise ValueError(
                f"Insufficient balance. "
                f"Need ₦{total_charge/100:.2f} "
                f"(₦{job_value_kobo/100:.2f} + "
                f"₦{platform_fee/100:.2f} platform fee). "
                f"Top up ₦{shortfall/100:.2f} more."
            )

        # Deduct total (job value + fee) from employer
        wallet.available_kobo -= total_charge
        wallet.locked_kobo    += total_charge

        escrow = EscrowRecord(
            job_id             = job_id,
            employer_id        = employer_id,
            worker_id          = worker_id,
            total_kobo         = total_charge,
            worker_amount_kobo = worker_amount,
            platform_fee_kobo  = platform_fee,
            status             = "locked",
        )
        db.add(escrow)

        db.add(WalletTransaction(
            user_id       = employer_id,
            type          = "escrow_lock",
            amount_kobo   = -total_charge,
            balance_after = wallet.available_kobo,
            description   = (
                f"Escrow locked — Job ₦{job_value_kobo/100:.2f} "
                f"+ ₦{platform_fee/100:.2f} fee"
            ),
            job_id        = job_id,
        ))

        await db.commit()
        await db.refresh(escrow)
        return escrow

    # ── Step 3: Employer marks job complete — release escrow ───────

    @staticmethod
    async def release_escrow(
        db:          AsyncSession,
        job_id:      str,
        employer_id: str,
    ) -> EscrowRecord:
        """
        Worker receives 100% of job value.
        Platform fee already collected from employer upfront.
        """
        result = await db.execute(
            select(EscrowRecord).where(
                EscrowRecord.job_id      == job_id,
                EscrowRecord.employer_id == employer_id,
                EscrowRecord.status      == "locked",
            )
        )
        escrow = result.scalar_one_or_none()
        if not escrow:
            raise ValueError("No active escrow found for this job.")

        # 1. Release employer locked balance
        emp_result = await db.execute(
            select(EmployerWallet).where(
                EmployerWallet.user_id == employer_id
            )
        )
        emp_wallet = emp_result.scalar_one()
        emp_wallet.locked_kobo  -= escrow.total_kobo
        emp_wallet.total_spent  += escrow.total_kobo

        # 2. Credit worker full job value (100%)
        wrk_result = await db.execute(
            select(WorkerWallet).where(
                WorkerWallet.user_id == escrow.worker_id
            )
        )
        wrk_wallet = wrk_result.scalar_one_or_none()
        if not wrk_wallet:
            wrk_wallet = WorkerWallet(user_id=escrow.worker_id)
            db.add(wrk_wallet)

        wrk_wallet.available_kobo += escrow.worker_amount_kobo
        wrk_wallet.total_earned   += escrow.worker_amount_kobo

        # 3. Update escrow
        escrow.status      = "released"
        escrow.released_at = datetime.utcnow()

        # 4. Log — worker credit
        db.add(WalletTransaction(
            user_id       = escrow.worker_id,
            type          = "escrow_release",
            amount_kobo   = escrow.worker_amount_kobo,
            balance_after = wrk_wallet.available_kobo,
            description   = f"Full payment for job {job_id}",
            job_id        = job_id,
            escrow_id     = escrow.id,
        ))

        # 5. Log — platform fee (internal record only)
        db.add(WalletTransaction(
            user_id       = employer_id,
            type          = "platform_fee",
            amount_kobo   = escrow.platform_fee_kobo,
            balance_after = emp_wallet.available_kobo,
            description   = f"2% platform fee collected for job {job_id}",
            job_id        = job_id,
            escrow_id     = escrow.id,
        ))

        await db.commit()
        await db.refresh(escrow)
        return escrow

    # ── Step 4: Worker withdrawal ──────────────────────────────────

    @staticmethod
    async def initiate_withdrawal(
        db:             AsyncSession,
        worker_id:      str,
        amount_kobo:    int,
        bank_code:      str,
        account_number: str,
        account_name:   str,
    ) -> dict:
        from app.models import Withdrawal
        from app.services.squad_service import SquadService

        if amount_kobo < Env.min_withdrawal_kobo:
            raise ValueError(
                f"Minimum withdrawal is ₦{Env.min_withdrawal_kobo // 100}"
            )

        result = await db.execute(
            select(WorkerWallet).where(WorkerWallet.user_id == worker_id)
        )
        wallet = result.scalar_one_or_none()
        if not wallet or wallet.available_kobo < amount_kobo:
            raise ValueError("Insufficient balance.")

        # Deduct immediately (hold during processing)
        wallet.available_kobo  -= amount_kobo
        wallet.total_withdrawn += amount_kobo

        reference = SquadService.generate_ref("HUSTLE_WD")

        # Log withdrawal
        withdrawal = Withdrawal(
            user_id        = worker_id,
            amount_kobo    = amount_kobo,
            bank_code      = bank_code,
            account_number = account_number,
            account_name   = account_name,
            squad_ref      = reference,
            status         = "processing",
        )
        db.add(withdrawal)

        db.add(WalletTransaction(
            user_id      = worker_id,
            type         = "withdrawal",
            amount_kobo  = -amount_kobo,
            balance_after = wallet.available_kobo,
            reference    = reference,
            description  = f"Withdrawal to {account_name} - {bank_code}",
        ))

        await db.commit()

        # Initiate Squad transfer
        try:
            squad_resp = await SquadService.transfer_to_bank(
                amount_kobo    = amount_kobo,
                bank_code      = bank_code,
                account_number = account_number,
                account_name   = account_name,
                narration      = "Hustle earnings payout",
                reference      = reference,
            )
            withdrawal.status = "completed"
            await db.commit()
            return {"status": "success", "reference": reference}

        except Exception as e:
            # Refund worker on failure
            wallet.available_kobo  += amount_kobo
            wallet.total_withdrawn -= amount_kobo
            withdrawal.status         = "failed"
            withdrawal.failure_reason = str(e)
            await db.commit()
            raise ValueError(f"Transfer failed: {e}")