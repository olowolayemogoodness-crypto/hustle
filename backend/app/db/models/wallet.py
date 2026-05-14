import uuid
from datetime import datetime
from sqlalchemy import BigInteger, String, ForeignKey, Text, TIMESTAMP
from sqlalchemy.orm import Mapped, mapped_column
from app.db.models.base import Base


class EmployerWallet(Base):
    __tablename__ = "employer_wallets"

    user_id:         Mapped[str] = mapped_column(String, ForeignKey("users.id"), primary_key=True)
    available_kobo:  Mapped[int] = mapped_column(BigInteger, default=0)
    locked_kobo:     Mapped[int] = mapped_column(BigInteger, default=0)
    total_spent:     Mapped[int] = mapped_column(BigInteger, default=0)
    updated_at:      Mapped[datetime] = mapped_column(TIMESTAMP(timezone=True), default=datetime.utcnow)


class WorkerWallet(Base):
    __tablename__ = "worker_wallets"

    user_id:          Mapped[str] = mapped_column(String, ForeignKey("users.id"), primary_key=True)
    available_kobo:   Mapped[int] = mapped_column(BigInteger, default=0)
    total_earned:     Mapped[int] = mapped_column(BigInteger, default=0)
    total_withdrawn:  Mapped[int] = mapped_column(BigInteger, default=0)
    updated_at:       Mapped[datetime] = mapped_column(TIMESTAMP(timezone=True), default=datetime.utcnow)


class WalletTransaction(Base):
    __tablename__ = "wallet_transactions"

    id:            Mapped[str] = mapped_column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id:       Mapped[str] = mapped_column(String, ForeignKey("users.id"), nullable=False)
    type:          Mapped[str] = mapped_column(String(30), nullable=False)
    amount_kobo:   Mapped[int] = mapped_column(BigInteger, nullable=False)
    balance_after: Mapped[int] = mapped_column(BigInteger, nullable=False)
    reference:     Mapped[str] = mapped_column(String(100), unique=True, nullable=True)
    description:   Mapped[str] = mapped_column(Text, nullable=True)
    job_id:        Mapped[str] = mapped_column(String, nullable=True)
    escrow_id:     Mapped[str] = mapped_column(String, nullable=True)
    status:        Mapped[str] = mapped_column(String(20), default="completed")
    created_at:    Mapped[datetime] = mapped_column(TIMESTAMP(timezone=True), default=datetime.utcnow)


class Withdrawal(Base):
    __tablename__ = "withdrawals"

    id:             Mapped[str] = mapped_column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id:        Mapped[str] = mapped_column(String, ForeignKey("users.id"), nullable=False)
    amount_kobo:    Mapped[int] = mapped_column(BigInteger, nullable=False)
    bank_code:      Mapped[str] = mapped_column(String(10), nullable=False)
    account_number: Mapped[str] = mapped_column(String(20), nullable=False)
    account_name:   Mapped[str] = mapped_column(String(100), nullable=True)
    squad_ref:      Mapped[str] = mapped_column(String(100), unique=True, nullable=True)
    status:         Mapped[str] = mapped_column(String(20), default="pending")
    failure_reason: Mapped[str] = mapped_column(Text, nullable=True)
    initiated_at:   Mapped[datetime] = mapped_column(TIMESTAMP(timezone=True), default=datetime.utcnow)
    completed_at:   Mapped[datetime] = mapped_column(TIMESTAMP(timezone=True), nullable=True)
