from typing import Optional

from pydantic import BaseModel, Field, conint, confloat


class FeedbackRequest(BaseModel):
    match_log_id: str = Field(..., description="The ID of the logged match event")
    completed: bool = Field(..., description="Whether the work was completed successfully")
    dispute_occurred: bool = Field(
        default=False,
        description="Whether a dispute or failure occurred during the job",
    )
    employer_rating: Optional[confloat(ge=0.0, le=5.0)] = Field(
        default=None,
        description="Rating given by the employer for the worker",
    )
    worker_rating: Optional[confloat(ge=0.0, le=5.0)] = Field(
        default=None,
        description="Rating given by the worker about the job",
    )


class FeedbackResponse(BaseModel):
    match_log_id: str
    completed: bool
    dispute_occurred: bool
    employer_rating: Optional[float]
    worker_rating: Optional[float]
    worker_updated_trust: Optional[float] = None
