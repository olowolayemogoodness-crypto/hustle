"""
Event-based match logging — immutable event records.
Decoupled from matching logic, won't crash if persistence fails.
"""
import json
from dataclasses import dataclass, asdict
from typing import Any, List

from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models.match_log import MatchLog
from app.schemas.match import WorkerScore
from app.services.uuid_utils import parse_uuid


@dataclass
class MatchEventRecord:
    """Immutable match event record."""
    job_id: Any
    worker_id: Any
    final_score: float
    rule_score: float
    ml_probability: float
    confidence: float
    risk_penalty: float
    completion_risk_probability: float | None = None
    risk_factors: str | None = None
    status: str = "ranked"


def worker_scores_to_events(
    job_id: Any,
    ranked_workers: List[WorkerScore],
) -> List[MatchEventRecord]:
    """Convert ranked WorkerScore objects to immutable event records."""
    events: List[MatchEventRecord] = []
    
    parsed_job_id = parse_uuid(job_id)
    for worker in ranked_workers:
        raw_risk_factors = worker.metadata.get("risk_factors")
        serialized_risk_factors = None
        if isinstance(raw_risk_factors, (dict, list)):
            serialized_risk_factors = json.dumps(raw_risk_factors)
        elif raw_risk_factors is not None:
            serialized_risk_factors = str(raw_risk_factors)

        event = MatchEventRecord(
            job_id=parsed_job_id,
            worker_id=parse_uuid(worker.worker_id),
            final_score=worker.final_score,
            rule_score=worker.rule_score,
            ml_probability=worker.ml_probability,
            confidence=worker.confidence,
            risk_penalty=worker.risk_penalty,
            completion_risk_probability=worker.metadata.get("completion_risk_probability"),
            risk_factors=serialized_risk_factors,
            status="ranked",
        )
        events.append(event)
    
    return events


async def persist_match_events(
    session: AsyncSession,
    events: List[MatchEventRecord],
) -> int:
    """
    Persist match events to database.
    
    Returns:
        Number of events persisted
    """
    if not events:
        return 0

    logs = [
        MatchLog(**asdict(event))
        for event in events
    ]

    session.add_all(logs)
    try:
        await session.commit()
        return len(logs)
    except SQLAlchemyError:
        await session.rollback()
        raise
