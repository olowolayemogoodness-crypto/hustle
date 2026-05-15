import uuid

from sqlalchemy import String, Float, Integer, DateTime, Text, JSON, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.sql import func

from app.db.types import GUID

from app.core.config import settings
from app.db.models.base import Base


class Job(Base):
    __tablename__ = "jobs"

    id: Mapped[uuid.UUID] = mapped_column(
        GUID(),
        primary_key=True,
        default=uuid.uuid4,
    )

    employer_id: Mapped[uuid.UUID] = mapped_column(
        GUID(),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
    )

    title: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
    )

    description: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )

    required_skills: Mapped[list[str]] = mapped_column(
        JSON,
        default=list,
    )

    latitude: Mapped[float | None] = mapped_column(Float, nullable=True)
    longitude: Mapped[float | None] = mapped_column(Float, nullable=True)
    budget: Mapped[float | None] = mapped_column(Float, nullable=True)
    urgency: Mapped[int | None] = mapped_column(Integer, nullable=True)

    status: Mapped[str] = mapped_column(
        String(20),
        default="open",
        nullable=False,
    )

    location_name: Mapped[str | None] = mapped_column(
        String(255),
        nullable=True,
    )

    pay_per_worker: Mapped[int] = mapped_column(
        Integer,
        default=0,
    )

    workers_needed: Mapped[int] = mapped_column(
        Integer,
        default=1,
    )

    workers_hired: Mapped[int] = mapped_column(
        Integer,
        default=0,
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

    employer = relationship("User", back_populates="job_postings")

    applications = relationship(
        "Application",
        back_populates="job",
    )
# patch — add status column if not present
from sqlalchemy import event
