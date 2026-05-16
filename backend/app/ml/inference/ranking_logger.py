"""
Structured logging for ranking decisions.
Provides full transparency into matching engine decisions.
"""
from __future__ import annotations

import json
import logging
from typing import Optional

from app.ml.inference.ranking_trace import RankingTrace

logger = logging.getLogger(__name__)


class RankingDecisionLogger:
    """Logs ranking decisions with full transparency."""

    def __init__(self, enable_debug: bool = False):
        self.enable_debug = enable_debug

    def log_ranking_decision(
        self,
        trace: RankingTrace,
        threshold_met: bool = True,
    ) -> None:
        """
        Log a single worker ranking decision.
        
        Args:
            trace: Complete ranking trace
            threshold_met: Whether worker passed scoring threshold
        """
        if not self.enable_debug:
            return

        log_data = {
            "event": "ranking_decision",
            "job_id": trace.job_id,
            "worker_id": trace.worker_id,
            "scores": {
                "rule_score": round(trace.rule_score, 1),
                "ml_acceptance_raw": round(trace.ml_acceptance_raw, 3),
                "ml_acceptance_calibrated": round(trace.ml_acceptance_calibrated, 3),
                "risk_probability_raw": round(trace.risk_probability_raw, 3),
                "risk_probability_calibrated": round(trace.risk_probability_calibrated, 3),
                "risk_penalty": round(trace.risk_penalty, 2),
                "final_score": round(trace.final_score, 1),
            },
            "fallbacks": {
                "ml_acceptance": trace.ml_acceptance_fallback,
                "risk_model": trace.risk_model_fallback,
            },
            "passed_threshold": threshold_met,
        }

        logger.debug(f"Ranking: {json.dumps(log_data)}")

    def log_matching_summary(
        self,
        job_id: str,
        total_workers: int,
        ranked_count: int,
        model_failures: Optional[dict] = None,
    ) -> None:
        """Log summary of matching job."""
        if not self.enable_debug:
            return

        summary = {
            "event": "matching_summary",
            "job_id": job_id,
            "total_workers_evaluated": total_workers,
            "workers_ranked": ranked_count,
        }

        if model_failures:
            summary["model_failures"] = model_failures

        logger.debug(f"Matching Summary: {json.dumps(summary)}")

    def log_trace_error(
        self,
        job_id: str,
        worker_id: str,
        error: str,
    ) -> None:
        """Log errors during trace creation."""
        logger.warning(
            f"Ranking Trace Error: job={job_id}, worker={worker_id}, error={error}"
        )


# Default global instance
_default_logger = RankingDecisionLogger(enable_debug=False)


def get_ranking_logger(enable_debug: bool = False) -> RankingDecisionLogger:
    """Get a configured ranking logger."""
    return RankingDecisionLogger(enable_debug=enable_debug)


def set_default_logger(logger: RankingDecisionLogger) -> None:
    """Set the default logger instance."""
    global _default_logger
    _default_logger = logger


def log_ranking_decision(
    trace: RankingTrace,
    threshold_met: bool = True,
) -> None:
    """Log using default logger."""
    _default_logger.log_ranking_decision(trace, threshold_met)
