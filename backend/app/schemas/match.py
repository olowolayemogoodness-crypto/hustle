from typing import Any, Dict, List, Literal, Optional
from pydantic import BaseModel, ConfigDict, Field
from app.schemas.job import JobBase
from app.schemas.worker import WorkerResponse


class MatchRequest(BaseModel):
    job: JobBase
    workers: List[WorkerResponse]


class MatchExplanation(BaseModel):
    strengths: List[str]
    warnings: List[str]


class WorkerScore(BaseModel):
    """Structured worker score from ranking engine."""
    worker_id: int
    final_score: float = Field(..., ge=0.0, le=1.0)
    rule_score: float = Field(..., ge=0.0, le=1.0)
    ml_probability: float = Field(..., ge=0.0, le=1.0)
    risk_penalty: float = Field(..., ge=0.0, le=1.0)
    confidence: float = Field(..., ge=0.0, le=1.0)
    trust_score: float = Field(default=0.5, ge=0.0, le=1.0)
    profile_completeness: float = Field(default=0.0, ge=0.0, le=1.0)
    
    explanation: MatchExplanation
    metadata: Dict[str, Any] = Field(default_factory=dict)


class MatchResponse(BaseModel):
    """Response from matching engine with ranked workers and recommendations."""
    model_config = ConfigDict(populate_by_name=True)

    job_id: int
    ranked_workers: List[WorkerScore] = Field(default_factory=list)
    matches: List[WorkerScore] = Field(default_factory=list)
    recommended_worker_ids: List[int] = Field(
        default_factory=list,
        description="Top workers recommended for selection (multi-worker support)",
    )


class AcceptMatchRequest(BaseModel):
    job_id: int
    worker_id: int


class AcceptMatchResponse(BaseModel):
    match_log_id: str
    accepted: bool


class MatchHistoryEntry(BaseModel):
    worker_id: str
    final_score: float
    rule_score: float
    ml_probability: float
    risk_penalty: float
    confidence: float
    status: str
    accepted: bool
    completed: bool
    dispute_occurred: bool
    employer_rating: float | None = None
    worker_rating: float | None = None
    created_at: str | None = None
    updated_at: str | None = None


class MatchHistoryResponse(BaseModel):
    job_id: str
    matches: List[MatchHistoryEntry] = Field(default_factory=list)


class MatchStatusUpdate(BaseModel):
    """Update match status without rejection semantics."""
    match_log_id: str
    status: Literal["viewed", "selected", "archived"] = "viewed"


class MatchStatusResponse(BaseModel):
    match_log_id: str
    status: Literal["viewed", "selected", "archived"]
    message: str
