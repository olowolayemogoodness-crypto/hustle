from typing import List
from pydantic import BaseModel
from app.schemas.job import JobBase
from app.schemas.worker import WorkerResponse


class MatchRequest(BaseModel):
    job: JobBase
    workers: List[WorkerResponse]


class MatchResult(BaseModel):
    worker_id: int
    final_score: float
    trust_score: float
    ml_probability: float
    explanation: List[str]


class MatchResponse(BaseModel):
    matches: List[MatchResult] = []
