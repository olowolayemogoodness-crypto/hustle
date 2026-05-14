import uuid
from sqlalchemy import Column, String, Boolean, DateTime, Integer, ForeignKey, func
from sqlalchemy.dialects.postgresql import UUID
from app.db.base import Base


class EmployerWallet(Base):
    __tablename__ = "employer_wallets"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False, unique=True)
    available_kobo = Column(Integer, default=0, nullable=False)
    locked_kobo = Column(Integer, default=0, nullable=False)
    total_spent = Column(Integer, default=0, nullable=False)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())


class WorkerWallet(Base):
    __tablename__ = "worker_wallets"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False, unique=True)
    available_kobo = Column(Integer, default=0, nullable=False)
    total_earned = Column(Integer, default=0, nullable=False)
    total_withdrawn = Column(Integer, default=0, nullable=False)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())


class WalletTransaction(Base):
    __tablename__ = "wallet_transactions"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    type = Column(String, nullable=False)  # topup | escrow_lock | escrow_release | platform_fee | withdrawal
    amount_kobo = Column(Integer, nullable=False)
    balance_after = Column(Integer, nullable=False)
    reference = Column(String, nullable=True, unique=True)
    description = Column(String, nullable=True)
    job_id = Column(String, nullable=True)
    escrow_id = Column(UUID(as_uuid=True), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())


class Withdrawal(Base):
    __tablename__ = "withdrawals"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    amount_kobo = Column(Integer, nullable=False)
    bank_code = Column(String, nullable=False)
    account_number = Column(String, nullable=False)
    account_name = Column(String, nullable=False)
    squad_ref = Column(String, nullable=True)
    status = Column(String, default="pending")  # pending | processing | completed | failed
    failure_reason = Column(String, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())


class EscrowRecord(Base):
    __tablename__ = "escrow_records"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    job_id = Column(String, nullable=False)
    employer_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    worker_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    total_kobo = Column(Integer, nullable=False)
    worker_amount_kobo = Column(Integer, nullable=False)
    platform_fee_kobo = Column(Integer, nullable=False)
    status = Column(String, default="locked")  # locked | released | refunded
    released_at = Column(DateTime(timezone=True), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
