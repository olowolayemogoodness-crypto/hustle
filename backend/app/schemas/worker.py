from pydantic import BaseModel
from typing import List, Optional


class WorkerBase(BaseModel):
    id: int
    name: str
    skills: List[str]

    # Core ML features
    rating: float  # 0–5
    completion_rate: float  # 0–1
    disputes: int
    verified: bool

    # Geo + availability
    latitude: float
    longitude: float
    availability: float  # 0–1 (how free they are)


class WorkerResponse(WorkerBase):
    trust_score: Optional[float] = None