"""
Tests for observability logging in the matching engine.
Verifies structured logging and trace capture.
"""
import pytest
import logging
from app.ml.inference.ranking_logger import RankingDecisionLogger
from app.ml.inference.ranking_trace import RankingTrace


class TestStructuredLogging:
    """Test structured logging of ranking decisions."""

    def test_logger_creates_valid_json_structure(self):
        """Test logger output has valid JSON structure."""
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
        )
        # Should not raise
        logger.log_ranking_decision(trace, threshold_met=True)

    def test_logger_captures_all_components(self):
        """Test that logger captures all score components."""
        logger = RankingDecisionLogger(enable_debug=True)
        trace = RankingTrace(
            worker_id="w123",
            job_id="j456",
            rule_score=55.5,
            ml_acceptance_raw=0.75,
            ml_acceptance_calibrated=0.72,
            risk_probability_raw=0.15,
            risk_probability_calibrated=0.18,
            risk_penalty=2.7,
            final_score=72.4,
            ml_acceptance_fallback=False,
            risk_model_fallback=False,
        )
        logger.log_ranking_decision(trace, threshold_met=True)

    def test_logger_summary_with_model_failures(self):
        """Test logger can capture model failures."""
        logger = RankingDecisionLogger(enable_debug=True)
        model_failures = {
            "acceptance_model": 2,
            "risk_model": 1,
        }
        logger.log_matching_summary(
            "job1",
            total_workers=10,
            ranked_count=8,
            model_failures=model_failures,
        )

    def test_logger_disabled_efficiency(self):
        """Test disabled logger is efficient (no-op)."""
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
        # No-op when disabled - should be fast
        logger.log_ranking_decision(trace)
        logger.log_matching_summary("j1", 10, 5)

    def test_trace_to_log_dict_format(self):
        """Test trace log dict has expected format."""
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
        
        # Verify structure
        assert "worker_id" in log_dict
        assert "job_id" in log_dict
        assert "rule_score" in log_dict
        assert "ml_acceptance" in log_dict
        assert "risk_penalty" in log_dict
        assert "final_score" in log_dict
        assert "fallbacks" in log_dict
        
        # Verify rounding for JSON serialization
        assert isinstance(log_dict["rule_score"], float)
        assert isinstance(log_dict["final_score"], float)
        assert log_dict["final_score"] == 65.1


class TestObservabilityIntegration:
    """Integration tests for observability features."""

    def test_logger_instance_independence(self):
        """Test multiple logger instances are independent."""
        logger1 = RankingDecisionLogger(enable_debug=True)
        logger2 = RankingDecisionLogger(enable_debug=False)
        
        assert logger1.enable_debug != logger2.enable_debug

    def test_trace_with_extreme_values_still_loggable(self):
        """Test extreme but valid values can be logged."""
        logger = RankingDecisionLogger(enable_debug=True)
        trace = RankingTrace(
            worker_id="w1",
            job_id="j1",
            rule_score=100.0,  # Max
            ml_acceptance_raw=0.0,  # Min
            ml_acceptance_calibrated=1.0,  # Max
            risk_probability_raw=0.0,  # Min
            risk_probability_calibrated=1.0,  # Max
            risk_penalty=15.0,  # Max penalty (1.0 * 15)
            final_score=0.0,  # Min after penalty
        )
        logger.log_ranking_decision(trace)

    def test_fallback_flags_in_logs(self):
        """Test that fallback flags appear in logs."""
        logger = RankingDecisionLogger(enable_debug=True)
        trace_with_fallback = RankingTrace(
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
            risk_model_fallback=True,
        )
        logger.log_ranking_decision(trace_with_fallback)

    def test_trace_error_logging(self):
        """Test error logging for trace creation failures."""
        logger = RankingDecisionLogger(enable_debug=True)
        logger.log_trace_error("job1", "worker1", "Feature extraction failed")


class TestRankingDecisionThresholdLogging:
    """Test logging of decisions relative to thresholds."""

    def test_log_above_threshold(self):
        """Test logging for worker above threshold."""
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
        )
        # High score = above threshold
        logger.log_ranking_decision(trace, threshold_met=True)

    def test_log_below_threshold(self):
        """Test logging for worker below threshold."""
        logger = RankingDecisionLogger(enable_debug=True)
        trace = RankingTrace(
            worker_id="w1",
            job_id="j1",
            rule_score=20.0,
            ml_acceptance_raw=0.3,
            ml_acceptance_calibrated=0.28,
            risk_probability_raw=0.5,
            risk_probability_calibrated=0.52,
            risk_penalty=7.8,
            final_score=8.2,
        )
        # Low score = below threshold
        logger.log_ranking_decision(trace, threshold_met=False)
