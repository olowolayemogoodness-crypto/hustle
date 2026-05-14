import uuid

from geoalchemy2 import Geography

from sqlalchemy import (
    String,
    Float,
    Integer,
    Boolean,
    ForeignKey,
    DateTime,
    Text,
    JSON,
)

from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.sql import func

from app.db.types import GUID

from app.core.config import settings
from app.db.models.base import Base


class WorkerProfile(Base):
    __tablename__ = "worker_profiles"

    id: Mapped[uuid.UUID] = mapped_column(
        GUID(),
        primary_key=True,
        default=uuid.uuid4,
    )

    user_id: Mapped[uuid.UUID] = mapped_column(
        GUID(),
        ForeignKey("users.id", ondelete="CASCADE"),
        unique=True,
        nullable=False,
    )

    skills: Mapped[list[str]] = mapped_column(
        JSON,
        default=list,
    )

    experience_level: Mapped[str] = mapped_column(
        String(20),
        default="entry",
    )

    job_radius_km: Mapped[int] = mapped_column(
        Integer,
        default=5,
    )

    availability: Mapped[str] = mapped_column(
        String(20),
        default="both",
    )

    bio: Mapped[str | None] = mapped_column(Text)

    trust_score: Mapped[float] = mapped_column(
        Float,
        default=50.0,
    )

    completion_rate: Mapped[float] = mapped_column(
        Float,
        default=0.0,
    )

    avg_rating: Mapped[float] = mapped_column(
        Float,
        default=0.0,
    )

    total_jobs: Mapped[int] = mapped_column(
        Integer,
        default=0,
    )

    disputes_count: Mapped[int] = mapped_column(
        Integer,
        default=0,
    )

    is_verified: Mapped[bool] = mapped_column(
        Boolean,
        default=False,
    )

    is_available: Mapped[bool] = mapped_column(
        Boolean,
        default=True,
    )

    fcm_token: Mapped[str | None] = mapped_column(
        String(255),
        nullable=True,
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

    LocationType = Geography(geometry_type="POINT", srid=4326)
    if settings.database_url.startswith("sqlite"):
        LocationType = String(255)

    last_location = mapped_column(
        LocationType,
        nullable=True,
    )

    user = relationship(
        "User",
        back_populates="worker_profile",
    )
