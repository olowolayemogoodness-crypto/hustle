import pytest

from app.ml.ranking import rank_workers


class TestRanking:
    def test_sorted_order_correct(self):
        results = [
            {"worker_id": 1, "final_score": 0.5, "confidence": 0.8, "trust_score": 0.7, "ml_probability": 0.6},
            {"worker_id": 2, "final_score": 0.8, "confidence": 0.9, "trust_score": 0.8, "ml_probability": 0.7},
            {"worker_id": 3, "final_score": 0.6, "confidence": 0.7, "trust_score": 0.6, "ml_probability": 0.5},
        ]
        ranked = rank_workers(results)
        assert ranked[0]["worker_id"] == 2  # Highest score first
        assert ranked[1]["worker_id"] == 3
        assert ranked[2]["worker_id"] == 1

    def test_higher_score_always_ranks_higher(self):
        results = [
            {"worker_id": 1, "final_score": 0.9, "confidence": 0.5, "trust_score": 0.5, "ml_probability": 0.5},
            {"worker_id": 2, "final_score": 0.1, "confidence": 0.9, "trust_score": 0.9, "ml_probability": 0.9},
        ]
        ranked = rank_workers(results)
        assert ranked[0]["worker_id"] == 1  # Higher final_score wins even with lower others
        assert ranked[1]["worker_id"] == 2

    def test_rank_field_added(self):
        results = [
            {"worker_id": 1, "final_score": 0.8},
            {"worker_id": 2, "final_score": 0.6},
        ]
        ranked = rank_workers(results)
        assert ranked[0]["rank"] == 1
        assert ranked[1]["rank"] == 2

    def test_empty_results(self):
        ranked = rank_workers([])
        assert ranked == []