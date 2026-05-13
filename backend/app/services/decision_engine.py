"""
Decision engine — selects top workers from ranked list.
Supports multi-worker selection for employer hiring workflow.
"""
from typing import List

from app.schemas.match import WorkerScore


def select_recommended_workers(
    ranked_workers: List[WorkerScore],
    max_recommended: int = 3,
    min_score_threshold: float = 0.6,
) -> List[int]:
    """
    Select top workers from ranked list based on score threshold.
    
    Args:
        ranked_workers: Pre-ranked workers from matching engine
        max_recommended: Maximum number to recommend
        min_score_threshold: Minimum final_score to include
    
    Returns:
        List of recommended worker IDs in order
    """
    recommended = []
    
    for worker in ranked_workers:
        if len(recommended) >= max_recommended:
            break
        
        if worker.final_score >= min_score_threshold:
            recommended.append(worker.worker_id)
    
    return recommended


def get_top_worker(ranked_workers: List[WorkerScore]) -> int | None:
    """Get single top-ranked worker ID."""
    if ranked_workers:
        return ranked_workers[0].worker_id
    return None
