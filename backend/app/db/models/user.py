import uuid

from sqlalchemy import String, Boolean, DateTime
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.sql import func

from app.db.types import GUID

from app.db.models.base import Base


class User(Base):
    __tablename__ = "users"

    id: Mapped[uuid.UUID] = mapped_column(
        GUID(),
        primary_key=True,
        default=uuid.uuid4,
    )

    phone: Mapped[str] = mapped_column(
        String(20),
        unique=True,
        nullable=False,
    )

    email: Mapped[str | None] = mapped_column(
        String(255),
        unique=True,
        nullable=True,
    )

    nin: Mapped[str | None] = mapped_column(
        String(11),
        unique=True,
        nullable=True,
    )

    full_name: Mapped[str | None] = mapped_column(
        String(100),
        nullable=True,
    )

    avatar_url: Mapped[str | None] = mapped_column(
        String(255),
        nullable=True,
    )

    role: Mapped[str | None] = mapped_column(
        String(20),
        nullable=True,
    )

    kyc_status: Mapped[str] = mapped_column(
        String(20),
        default="unverified",
    )

    is_active: Mapped[bool] = mapped_column(
        Boolean,
        default=True,
    )

    created_at: Mapped[DateTime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
    )

    updated_at: Mapped[DateTime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
    )

    worker_profile = relationship(
        "WorkerProfile",
        back_populates="user",
        uselist=False,
    )

    employer_profile = relationship(
        "EmployerProfile",
        back_populates="user",
        uselist=False,
    )

    job_postings = relationship(
        "Job",
        back_populates="employer",
        foreign_keys="Job.employer_id",
    )

    applications = relationship(
        "Application",
        back_populates="worker",
        foreign_keys="Application.worker_id",
    )
