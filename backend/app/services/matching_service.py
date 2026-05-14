from typing import List

from app.core.logging import get_logger
from app.schemas.job import JobBase
from app.schemas.match import WorkerScore
from app.schemas.worker import WorkerResponse
from app.services.matching_engine import rank_candidates

logger = get_logger(__name__)


def match_workers(job: JobBase, workers: List[WorkerResponse]) -> List[WorkerScore]:
    """
    Match workers to a job using the pure matching engine.
    Handles logging and any side effects.
    """
    if not workers:
        logger.info("No workers supplied for job %s", job.id)
        return []

    # Use the pure matching engine for scoring
    ranked_workers = rank_candidates(job, workers)

    logger.info("Ranked %d workers for job %s", len(ranked_workers), job.id)

    return ranked_workers
