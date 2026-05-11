from pydantic import BaseModel
from typing import List


class PredictionResponse(BaseModel):
    worker_id: int

    final_score: float
    trust_score: float
    ml_probability: float

    explanation: List[str]