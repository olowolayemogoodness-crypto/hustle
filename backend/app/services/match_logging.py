from typing import Iterable

from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models.match_log import MatchLog
from app.services.uuid_utils import parse_uuid


def _safe_get(data: dict, key: str, default: float = 0.0) -> float:
    """Safely extract float values from result dict with fallback."""
    value = data.get(key, default)
    return float(value) if value is not None else default


async def log_match_batch(
    session: AsyncSession,
    job_id: int | str,
    ranked_results: Iterable[dict],
    chosen_worker_id: int | str | None = None,
) -> list[MatchLog]:
    logs: list[MatchLog] = []
    parsed_job_id = parse_uuid(job_id)

    for result in ranked_results:
        logs.append(
            MatchLog(
                job_id=parsed_job_id,
                worker_id=parse_uuid(result.get("worker_id", 0)),
                final_score=_safe_get(result, "final_score"),
                rule_score=_safe_get(result, "rule_score"),
                ml_probability=_safe_get(result, "ml_probability"),
                risk_penalty=_safe_get(result, "risk_penalty"),
                confidence=_safe_get(result, "confidence"),
                accepted=result.get("worker_id") == chosen_worker_id,
            )
        )

    session.add_all(logs)
    await session.commit()
    return logs
