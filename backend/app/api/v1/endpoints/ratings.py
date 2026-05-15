import uuid
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, desc
from pydantic import BaseModel, field_validator
from app.db.session import get_db
from app.db.models.user import User
from app.db.models.rating import Rating
from app.dependencies import get_current_user

router = APIRouter(prefix="/ratings", tags=["ratings"])


class RatingCreate(BaseModel):
    job_id:   str
    ratee_id: str
    score:    int
    comment:  str | None = None

    @field_validator("score")
    @classmethod
    def validate_score(cls, v: int) -> int:
        if v < 1 or v > 5:
            raise ValueError("Score must be between 1 and 5")
        return v


@router.post("")
async def submit_rating(
    body:         RatingCreate,
    current_user: User = Depends(get_current_user),
    db:           AsyncSession = Depends(get_db),
):
    # Prevent duplicate rating
    existing = await db.execute(
        select(Rating).where(
            Rating.job_id   == uuid.UUID(body.job_id),
            Rating.rater_id == current_user.id,
            Rating.ratee_id == uuid.UUID(body.ratee_id),
        )
    )
    if existing.scalar_one_or_none():
        raise HTTPException(
            status_code=400,
            detail="You have already rated this user for this job"
        )

    rating = Rating(
        job_id   = uuid.UUID(body.job_id),
        rater_id = current_user.id,
        ratee_id = uuid.UUID(body.ratee_id),
        score    = body.score,
        comment  = body.comment,
    )
    db.add(rating)
    await db.commit()
    await db.refresh(rating)

    return {
        "id":       str(rating.id),
        "job_id":   body.job_id,
        "ratee_id": body.ratee_id,
        "score":    rating.score,
        "comment":  rating.comment,
    }


@router.get("/{user_id}")
async def get_ratings(
    user_id:      str,
    current_user: User = Depends(get_current_user),
    db:           AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(Rating)
        .where(Rating.ratee_id == uuid.UUID(user_id))
        .order_by(desc(Rating.created_at))
    )
    ratings = result.scalars().all()

    avg = (
        sum(r.score for r in ratings) / len(ratings)
        if ratings else 0.0
    )

    return {
        "user_id":    user_id,
        "avg_rating": round(avg, 2),
        "total":      len(ratings),
        "data": [
            {
                "id":         str(r.id),
                "job_id":     str(r.job_id),
                "rater_id":   str(r.rater_id),
                "score":      r.score,
                "comment":    r.comment,
                "created_at": r.created_at.isoformat() if r.created_at else None,
            }
            for r in ratings
        ],
    }
