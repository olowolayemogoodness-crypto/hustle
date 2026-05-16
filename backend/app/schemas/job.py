from pydantic import BaseModel
from typing import List, Optional


class JobBase(BaseModel):
    id: str | int
    title: str
    description: str

    required_skills: List[str]

    latitude: Optional[float] = None
    longitude: Optional[float] = None

    budget: float
    urgency: int  # 1–5 scale