from pydantic import BaseModel, Field
from typing import List, Optional


class WorkerBase(BaseModel):
    id: str | int
    name: str
    skills: List[str]
    distance_km: Optional[float] = Field(None, ge=0)
    skill_overlap: Optional[float] = Field(None, ge=0, le=1)

    # Core ML features
    rating: float = Field(..., ge=0, le=5)
    completion_rate: float = Field(..., ge=0, le=1)
    disputes: int = Field(..., ge=0)
    verified: bool

    # Geo + availability
    latitude: float
    longitude: float
    availability: float = Field(..., ge=0, le=1)

    # Optional profile health fields for cold start and feedback
    bio: Optional[str] = None
    experience_level: Optional[str] = None
    recent_activity_days: Optional[int] = None
    completed_jobs: Optional[int] = None


class WorkerResponse(WorkerBase):
    trust_score: Optional[float] = None
