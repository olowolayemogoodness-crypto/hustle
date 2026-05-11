from pydantic import BaseModel
from typing import List
from app.schemas.worker import WorkerResponse
from app.schemas.job import JobBase


class MatchRequest(BaseModel):
    job: JobBase
    workers: List[WorkerResponse]