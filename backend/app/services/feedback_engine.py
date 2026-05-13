"""
Feedback engine — processes feedback to improve future rankings.
Converts outcome signals into worker reliability adjustments.
"""
from typing import Optional


def compute_performance_reward(
    completed: bool,
    dispute_occurred: bool,
    employer_rating: Optional[float],
    worker_rating: Optional[float],
) -> float:
    """
    Compute performance reward/penalty based on job outcome.
    
    Returns:
        Adjustment to trust score (-0.1 to +0.1)
    """
    reward = 0.0
    
    # Completion signal
    if completed:
        reward += 0.06  # Strong positive signal
    else:
        reward -= 0.10  # Strong negative signal
    
    # Dispute signal
    if dispute_occurred:
        reward -= 0.05  # Moderate negative
    
    # Rating signals (if provided)
    if employer_rating is not None:
        # Map 1-5 rating to adjustment
        normalized_rating = (employer_rating - 1.0) / 4.0  # [0, 1]
        reward += (normalized_rating - 0.5) * 0.08  # ±0.04
    
    if worker_rating is not None:
        normalized_rating = (worker_rating - 1.0) / 4.0
        reward += (normalized_rating - 0.5) * 0.04  # ±0.02 (less weight)
    
    # Clamp to reasonable bounds
    return max(-0.1, min(0.1, reward))


def apply_performance_signal(
    current_trust_score: float,
    reward: float,
    decay_factor: float = 0.95,
) -> float:
    """
    Apply performance reward to trust score with momentum.
    
    Args:
        current_trust_score: Current worker trust score [0, 1]
        reward: Performance reward [-0.1, 0.1]
        decay_factor: How much to weight new signal (0.95 = 5% new, 95% momentum)
    
    Returns:
        Updated trust score [0, 1]
    """
    updated = current_trust_score * decay_factor + (0.5 + reward) * (1 - decay_factor)
    return max(0.0, min(1.0, updated))


def compute_reliability_index(
    total_jobs: int,
    completed_jobs: int,
    avg_rating: float,
    disputes_count: int,
    trust_score: float,
) -> float:
    """
    Compute worker reliability index (used for future ranking adjustments).
    
    This is the signal that future ranking should use.
    
    Returns:
        Reliability index [0, 1]
    """
    if total_jobs == 0:
        return 0.5  # Neutral for new workers
    
    completion_rate = completed_jobs / total_jobs
    rating_score = avg_rating / 5.0 if avg_rating > 0 else 0.5
    dispute_penalty = min(disputes_count / 10.0, 1.0)  # Cap at 1.0
    
    # Weighted combination
    reliability = (
        0.40 * completion_rate +
        0.35 * rating_score +
        0.15 * trust_score +
        0.10 * (1.0 - dispute_penalty)
    )
    
    return max(0.0, min(1.0, reliability))
