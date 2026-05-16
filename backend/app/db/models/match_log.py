import uuid

from sqlalchemy import Boolean, Float, DateTime, ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column, deferred
from sqlalchemy.sql import func

from app.db.types import GUID

from app.db.models.base import Base


class MatchLog(Base):
    __tablename__ = "match_logs"

    id: Mapped[uuid.UUID] = mapped_column(
        GUID(),
        primary_key=True,
        default=uuid.uuid4,
    )

    job_id: Mapped[uuid.UUID] = mapped_column(
        GUID(),
        ForeignKey("jobs.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    worker_id: Mapped[uuid.UUID] = mapped_column(
        GUID(),
        ForeignKey("worker_profiles.user_id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    final_score: Mapped[float] = mapped_column(
        Float,
        nullable=False,
    )

    rule_score: Mapped[float] = mapped_column(
        Float,
        nullable=False,
    )

    ml_probability: Mapped[float] = mapped_column(
        Float,
        nullable=False,
    )

    risk_penalty: Mapped[float] = mapped_column(
        Float,
        nullable=False,
    )

    completion_risk_probability: Mapped[float | None] = mapped_column(
        Float,
        nullable=True,
    )

    risk_factors: Mapped[str | None] = deferred(mapped_column(
        String,
        nullable=True,
    ))

    status: Mapped[str] = mapped_column(
        String(20),
        default="ranked",
    )

    accepted: Mapped[bool] = mapped_column(
        Boolean,
        default=False,
    )

    completed: Mapped[bool] = mapped_column(
        Boolean,
        default=False,
    )

    dispute_occurred: Mapped[bool] = mapped_column(
        Boolean,
        default=False,
    )

    employer_rating: Mapped[float | None] = mapped_column(
        Float,
        nullable=True,
    )

    worker_rating: Mapped[float | None] = mapped_column(
        Float,
        nullable=True,
    )

    distance_km: Mapped[float | None] = deferred(mapped_column(
        Float,
        nullable=True,
    ))

    skill_overlap_ratio: Mapped[float | None] = deferred(mapped_column(
        Float,
        nullable=True,
    ))

    worker_completion_rate: Mapped[float | None] = deferred(mapped_column(
        Float,
        nullable=True,
    ))

    worker_trust_score: Mapped[float | None] = deferred(mapped_column(
        Float,
        nullable=True,
    ))

    years_experience: Mapped[int | None] = deferred(mapped_column(
        Integer,
        nullable=True,
    ))

    job_budget: Mapped[float | None] = deferred(mapped_column(
        Float,
        nullable=True,
    ))

    job_urgency: Mapped[int | None] = deferred(mapped_column(
        Integer,
        nullable=True,
    ))

    created_at: Mapped[DateTime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
    )

    updated_at: Mapped[DateTime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
    )

