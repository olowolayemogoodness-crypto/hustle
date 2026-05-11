from typing import Optional
from pydantic import BaseModel, Field


class PredictionInput(BaseModel):
    distance_km: Optional[float] = Field(None, ge=0)
    skill_overlap: Optional[float] = Field(None, ge=0, le=1)
    trust_score: Optional[float] = Field(None, ge=0, le=1)
    rating: Optional[float] = Field(None, ge=0, le=5)
    completion_rate: Optional[float] = Field(None, ge=0, le=1)
    disputes: Optional[int] = Field(None, ge=0)
    availability: Optional[float] = Field(None, ge=0, le=1)


class PredictionResponse(BaseModel):
    success_probability: float
