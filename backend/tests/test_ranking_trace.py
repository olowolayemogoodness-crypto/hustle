"""
Tests for ranking trace structure and observability.
Verifies that ranking traces capture all scoring components correctly.
"""
import pytest
from app.ml.inference.ranking_trace import RankingTrace
from app.ml.inference.ranking_logger import RankingDecisionLogger, get_ranking_logger


class TestRankingTrace:
    """Test RankingTrace data structure."""

    def test_trace_creation_valid(self):
        """Test creating a valid ranking trace."""
        trace = RankingTrace(
            worker_id="w1",
            job_id="j1",
            rule_score=50.0,
            ml_acceptance_raw=0.7,
            ml_acceptance_calibrated=0.65,
            risk_probability_raw=0.2,
            risk_probability_calibrated=0.25,
            risk_penalty=3.75,
            final_score=65.0,
        )
        assert trace.worker_id == "w1"
        assert trace.job_id == "j1"
        assert trace.rule_score == 50.0
        assert trace.final_score == 65.0
        assert not trace.ml_acceptance_fallback
        assert not trace.risk_model_fallback

    def test_trace_with_fallback_flags(self):
        """Test trace captures fallback flags."""
        trace = RankingTrace(
            worker_id="w1",
            job_id="j1",
            rule_score=50.0,
            ml_acceptance_raw=0.5,
            ml_acceptance_calibrated=0.5,
            risk_probability_raw=0.0,
            risk_probability_calibrated=0.0,
            risk_penalty=0.0,
            final_score=35.0,
            ml_acceptance_fallback=True,
            risk_model_fallback=False,
        )
        assert trace.ml_acceptance_fallback
        assert not trace.risk_model_fallback

    def test_trace_to_dict(self):
        """Test converting trace to dict."""
        trace = RankingTrace(
            worker_id="w1",
            job_id="j1",
            rule_score=50.0,
            ml_acceptance_raw=0.7,
            ml_acceptance_calibrated=0.65,
            risk_probability_raw=0.2,
            risk_probability_calibrated=0.25,
            risk_penalty=3.75,
            final_score=65.0,
        )
        d = trace.to_dict()
        assert d["worker_id"] == "w1"
        assert d["job_id"] == "j1"
        assert d["final_score"] == 65.0

    def test_trace_to_log_dict(self):
        """Test converting trace to log dict (minimal version)."""
        trace = RankingTrace(
            worker_id="w1",
            job_id="j1",
            rule_score=50.5,
            ml_acceptance_raw=0.7,
            ml_acceptance_calibrated=0.65,
            risk_probability_raw=0.2,
            risk_probability_calibrated=0.25,
            risk_penalty=3.75,
            final_score=65.123,
        )
        log_dict = trace.to_log_dict()
        assert "worker_id" in log_dict
        assert "final_score" in log_dict
        assert log_dict["final_score"] == 65.1  # Rounded

    def test_trace_validation_nan(self):
        """Test trace validation catches NaN."""
        with pytest.raises(ValueError, match="contains NaN or Inf"):
            RankingTrace(
                worker_id="w1",
                job_id="j1",
                rule_score=float('nan'),
                ml_acceptance_raw=0.7,
                ml_acceptance_calibrated=0.65,
                risk_probability_raw=0.2,
                risk_probability_calibrated=0.25,
                risk_penalty=3.75,
                final_score=65.0,
            )

    def test_trace_validation_inf(self):
        """Test trace validation catches Inf."""
        with pytest.raises(ValueError, match="contains NaN or Inf"):
            RankingTrace(
                worker_id="w1",
                job_id="j1",
                rule_score=50.0,
                ml_acceptance_raw=0.7,
                ml_acceptance_calibrated=float('inf'),
                risk_probability_raw=0.2,
                risk_probability_calibrated=0.25,
                risk_penalty=3.75,
                final_score=65.0,
            )

    def test_trace_score_clamping_boundaries(self):
        """Test trace accepts scores at boundary values."""
        # All values at 0
        trace1 = RankingTrace(
            worker_id="w1",
            job_id="j1",
            rule_score=0.0,
            ml_acceptance_raw=0.0,
            ml_acceptance_calibrated=0.0,
            risk_probability_raw=0.0,
            risk_probability_calibrated=0.0,
            risk_penalty=0.0,
            final_score=0.0,
        )
        assert trace1.final_score == 0.0

        # All values at max
        trace2 = RankingTrace(
            worker_id="w1",
            job_id="j1",
            rule_score=100.0,
            ml_acceptance_raw=1.0,
            ml_acceptance_calibrated=1.0,
            risk_probability_raw=1.0,
            risk_probability_calibrated=1.0,
            risk_penalty=15.0,
            final_score=100.0,
        )
        assert trace2.final_score == 100.0


class TestRankingLogger:
    """Test RankingDecisionLogger."""

    def test_logger_creation(self):
        """Test creating a logger."""
        logger = RankingDecisionLogger(enable_debug=True)
        assert logger.enable_debug

    def test_logger_get_default(self):
        """Test getting default logger."""
        logger = get_ranking_logger(enable_debug=False)
        assert not logger.enable_debug

    def test_logger_no_output_when_disabled(self):
        """Test logger produces no output when disabled."""
        logger = RankingDecisionLogger(enable_debug=False)
        trace = RankingTrace(
            worker_id="w1",
            job_id="j1",
            rule_score=50.0,
            ml_acceptance_raw=0.7,
            ml_acceptance_calibrated=0.65,
            risk_probability_raw=0.2,
            risk_probability_calibrated=0.25,
            risk_penalty=3.75,
            final_score=65.0,
        )
        # Should not raise even if logging is disabled
        logger.log_ranking_decision(trace)

    def test_logger_with_decision_metadata(self):
        """Test logger captures decision metadata."""
        logger = RankingDecisionLogger(enable_debug=True)
        trace = RankingTrace(
            worker_id="w1",
            job_id="j1",
            rule_score=50.0,
            ml_acceptance_raw=0.7,
            ml_acceptance_calibrated=0.65,
            risk_probability_raw=0.2,
            risk_probability_calibrated=0.25,
            risk_penalty=3.75,
            final_score=65.0,
            ml_acceptance_fallback=True,
        )
        # Should not raise
        logger.log_ranking_decision(trace, threshold_met=True)

    def test_logger_summary(self):
        """Test logger summary capture."""
        logger = RankingDecisionLogger(enable_debug=True)
        logger.log_matching_summary("job1", total_workers=10, ranked_count=5)

    def test_logger_error_handling(self):
        """Test logger error handling."""
        logger = RankingDecisionLogger(enable_debug=True)
        logger.log_trace_error("job1", "worker1", "Model not found")


class TestRankingTraceIntegration:
    """Integration tests for ranking trace with matching engine."""

    def test_trace_roundtrip_serialization(self):
        """Test trace serializes and deserializes correctly."""
        trace = RankingTrace(
            worker_id="w1",
            job_id="j1",
            rule_score=50.0,
            ml_acceptance_raw=0.7,
            ml_acceptance_calibrated=0.65,
            risk_probability_raw=0.2,
            risk_probability_calibrated=0.25,
            risk_penalty=3.75,
            final_score=65.0,
        )
        trace_dict = trace.to_dict()
        assert trace_dict["worker_id"] == trace.worker_id
        assert trace_dict["final_score"] == trace.final_score

    def test_multiple_traces_unique_per_worker(self):
        """Test different workers have different traces."""
        trace1 = RankingTrace(
            worker_id="w1",
            job_id="j1",
            rule_score=50.0,
            ml_acceptance_raw=0.7,
            ml_acceptance_calibrated=0.65,
            risk_probability_raw=0.2,
            risk_probability_calibrated=0.25,
            risk_penalty=3.75,
            final_score=65.0,
        )
        trace2 = RankingTrace(
            worker_id="w2",
            job_id="j1",
            rule_score=60.0,
            ml_acceptance_raw=0.8,
            ml_acceptance_calibrated=0.75,
            risk_probability_raw=0.1,
            risk_probability_calibrated=0.15,
            risk_penalty=2.25,
            final_score=75.0,
        )
        assert trace1.worker_id != trace2.worker_id
        assert trace1.final_score != trace2.final_score
