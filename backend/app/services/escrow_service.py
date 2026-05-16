from datetime import datetime
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.db.models.wallet import (
    EscrowRecord, EmployerWallet, WorkerWallet,
    WalletTransaction, Withdrawal,
)
import logging

logger = logging.getLogger(__name__)

PLATFORM_FEE_PERCENT = 2
MIN_WITHDRAWAL_KOBO  = 10000  # ₦100


def calculate_employer_charge(job_value_kobo: int) -> tuple[int, int, int]:
    platform_fee  = int(job_value_kobo * PLATFORM_FEE_PERCENT / 100)
    total_charge  = job_value_kobo + platform_fee
    worker_amount = job_value_kobo
    return total_charge, worker_amount, platform_fee


class EscrowService:

    @staticmethod
    async def credit_employer_wallet(
        db:          AsyncSession,
        user_id:     str,
        amount_kobo: int,
        squad_ref:   str,
    ) -> None:
        # Idempotency check
        existing = await db.execute(
            select(WalletTransaction).where(
                WalletTransaction.reference == squad_ref
            )
        )
        if existing.scalar_one_or_none():
            logger.warning(f"Duplicate webhook ref: {squad_ref}")
            return

        # Get or create employer wallet
        result = await db.execute(
            select(EmployerWallet).where(
                EmployerWallet.user_id == user_id
            )
        )
        wallet = result.scalar_one_or_none()
        if not wallet:
            wallet = EmployerWallet(user_id=user_id)
            db.add(wallet)
            await db.flush()

        wallet.available_kobo += amount_kobo

        db.add(WalletTransaction(
            user_id       = user_id,
            type          = "topup",
            amount        = amount_kobo,
            amount_kobo   = amount_kobo,
            balance_after = wallet.available_kobo,
            reference     = squad_ref,
            description   = "Wallet top-up via Squad",
        ))

        await db.commit()
        logger.info(f"✅ Credited ₦{amount_kobo/100:.2f} to {user_id}")


    @staticmethod
    async def lock_funds(
        db:             AsyncSession,
        job_id:         str,
        employer_id:    str,
        worker_id:      str,
        job_value_kobo: int,
    ) -> EscrowRecord:
        total_charge, worker_amount, platform_fee = \
            calculate_employer_charge(job_value_kobo)

        result = await db.execute(
            select(EmployerWallet).where(
                EmployerWallet.user_id == employer_id
            )
        )
        wallet = result.scalar_one_or_none()
        if not wallet or wallet.available_kobo < total_charge:
            shortfall = total_charge - (wallet.available_kobo if wallet else 0)
            raise ValueError(
                f"Insufficient balance. Need ₦{total_charge/100:.2f}. "
                f"Top up ₦{shortfall/100:.2f} more."
            )

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
            description   = f"Escrow locked — Job ₦{job_value_kobo/100:.2f} + ₦{platform_fee/100:.2f} fee",
            job_id        = job_id,
        ))

        await db.commit()
        await db.refresh(escrow)
        return escrow


    @staticmethod
    async def release_escrow(
        db:          AsyncSession,
        job_id:      str,
        employer_id: str,
    ) -> EscrowRecord:
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

        # Release employer locked balance
        emp_result = await db.execute(
            select(EmployerWallet).where(
                EmployerWallet.user_id == employer_id
            )
        )
        emp_wallet = emp_result.scalar_one()
        emp_wallet.locked_kobo -= escrow.total_kobo
        emp_wallet.total_spent += escrow.total_kobo

        # Credit worker
        wrk_result = await db.execute(
            select(WorkerWallet).where(
                WorkerWallet.user_id == escrow.worker_id
            )
        )
        wrk_wallet = wrk_result.scalar_one_or_none()
        if not wrk_wallet:
            wrk_wallet = WorkerWallet(user_id=escrow.worker_id)
            db.add(wrk_wallet)
            await db.flush()

        wrk_wallet.available_kobo += escrow.worker_amount_kobo
        wrk_wallet.total_earned   += escrow.worker_amount_kobo

        escrow.status      = "released"
        escrow.released_at = datetime.utcnow()

        db.add(WalletTransaction(
            user_id       = str(escrow.worker_id),
            type          = "escrow_release",
            amount        = escrow.worker_amount_kobo,
            amount_kobo   = escrow.worker_amount_kobo,
            balance_after = wrk_wallet.available_kobo,
            description   = f"Payment for job {job_id}",
            job_id        = job_id,
        ))

        db.add(WalletTransaction(
            user_id       = employer_id,
            type          = "platform_fee",
            amount        = escrow.platform_fee_kobo,
            amount_kobo   = escrow.platform_fee_kobo,
            balance_after = emp_wallet.available_kobo,
            description   = f"2% platform fee for job {job_id}",
            job_id        = job_id,
        ))

        await db.commit()
        await db.refresh(escrow)
        return escrow


    @staticmethod
    async def initiate_withdrawal(
        db:             AsyncSession,
        worker_id:      str,
        amount_kobo:    int,
        bank_code:      str,
        account_number: str,
        account_name:   str,
    ) -> dict:
        from app.services.squad_service import SquadService

        if amount_kobo < MIN_WITHDRAWAL_KOBO:
            raise ValueError(f"Minimum withdrawal is ₦{MIN_WITHDRAWAL_KOBO // 100}")

        result = await db.execute(
            select(WorkerWallet).where(WorkerWallet.user_id == worker_id)
        )
        wallet = result.scalar_one_or_none()
        if not wallet or wallet.available_kobo < amount_kobo:
            raise ValueError("Insufficient balance.")

        wallet.available_kobo  -= amount_kobo
        wallet.total_withdrawn += amount_kobo

        reference = SquadService.generate_ref("HUSTLE_WD")

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
            user_id       = worker_id,
            type          = "withdrawal",
            amount_kobo   = -amount_kobo,
            balance_after = wallet.available_kobo,
            reference     = reference,
            description   = f"Withdrawal to {account_name}",
        ))

        await db.commit()

        try:
            await SquadService.transfer_to_bank(
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
            wallet.available_kobo  += amount_kobo
            wallet.total_withdrawn -= amount_kobo
            withdrawal.status         = "failed"
            withdrawal.failure_reason = str(e)
            await db.commit()
            raise ValueError(f"Transfer failed: {e}")
