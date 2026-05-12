from pydantic import BaseModel
from typing import List


class JobBase(BaseModel):
    id: int
    title: str
    description: str

    required_skills: List[str]

    latitude: float
    longitude: float

    budget: float
    urgency: int  # 1–5 scale