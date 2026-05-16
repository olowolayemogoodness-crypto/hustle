import uuid
from datetime import datetime
from sqlalchemy import Boolean, ForeignKey, TIMESTAMP, Text, Numeric
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.sql import func
from app.db.types import GUID
from app.db.models.base import Base


class Application(Base):
    __tablename__ = "applications"

    id:            Mapped[uuid.UUID]   = mapped_column(GUID(), primary_key=True, default=uuid.uuid4)
    job_id:        Mapped[uuid.UUID]   = mapped_column(GUID(), ForeignKey("jobs.id", ondelete="CASCADE"), nullable=False)
    worker_id:     Mapped[uuid.UUID]   = mapped_column(GUID(), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    cover_letter:  Mapped[str | None]  = mapped_column(Text, nullable=True)
    proposed_rate: Mapped[float | None] = mapped_column(Numeric, nullable=True)
    is_accepted:   Mapped[bool]        = mapped_column(Boolean, default=False)
    created_at:    Mapped[datetime]    = mapped_column(TIMESTAMP(timezone=True), server_default=func.now())
    updated_at:    Mapped[datetime]    = mapped_column(TIMESTAMP(timezone=True), server_default=func.now())

    job    = relationship("Job",  back_populates="applications")
    worker = relationship("User", back_populates="applications", foreign_keys=[worker_id])
