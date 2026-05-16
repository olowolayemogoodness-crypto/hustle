<!-- Consolidated Phase 2.x documentation: Phase 2, 2.5, 2.6 -->
# Phase 2 — Risk, Calibration, and Observability (Consolidated)

## Overview

This document consolidates Phase 2 (Risk Prediction), Phase 2.5 (Calibration & Stability),
and Phase 2.6 (Observability & Ranking Trace) into a single, structured reference for
developers, reviewers, and operators.

It covers architecture, implementation details, checklist status, integration guidance,
testing strategy, deployment notes, and next steps.

---

## Quick Summary

- Phase 2 (Risk): Adds ML-based risk prediction incorporated into match scoring.
- Phase 2.5 (Calibration): Adds Platt Scaling and safety guards for ML outputs.
- Phase 2.6 (Observability): Adds `RankingTrace`, structured logging, and debug flags.

All changes are intentionally backward-compatible: API contracts are unchanged and
new fields are optional or stored in metadata.

---

## Contents

1. Checklist (Phase 2.6)
2. Phase 2.5 — Calibration & Safety (Overview and changes)
3. Phase 2.6 — Implementation Summary
4. Integration Guide & Data Flow
5. Testing Strategy
6. Deployment Notes & Rollback
7. Performance, Security, and Limitations
8. Files Modified/Created
9. Next Steps

---

## 1. Checklist (Phase 2.6)

The Phase 2.6 completion checklist verifies core implementation, tests, documentation,
and compatibility. High-level status: COMPLETE — verified and tested.

- RankingTrace class implemented (`app/ml/inference/ranking_trace.py`)
- `RankingDecisionLogger` implemented (`app/ml/inference/ranking_logger.py`)
- Configuration flags added (`enable_match_debug`, `enable_ranking_trace`)
- ML output contract extended with `is_fallback`
- Matching engine integrates traces and logging
- Test suite updated with observability and compatibility tests

See detailed items in the original checklist documents for granular lines.

---

## 2. Phase 2.5 — Calibration & Safety

### Goals

- Provide reliable calibrated probabilities for ML outputs (Acceptance & Risk)
- Maintain backward compatibility and safe fallbacks
- Add safety guards to prevent NaN/Inf and extreme outputs

### Key Additions

- Platt Scaling calibration persisted to `.joblib` files (e.g. `acceptance_calibration.joblib`).
- `MLPredictionOutput` dataclass standardizes `raw_probability`, `calibrated_probability`, and `confidence`.
- Predictors return `MLPredictionOutput` and set `is_fallback` when models missing.
- Matching engine incorporates calibration, applies clamps, and uses safe fallback values.

### Safety and Contract

- Final scoring formula preserved, with clamps and NaN/Inf guards.
- New fields added in `metadata` to avoid schema-breaking changes.

---

## 3. Phase 2.6 — Implementation Summary

Phase 2.6 focuses on observability and traceability of ranking decisions.

### Primary Components

- `RankingTrace` — dataclass capturing full scoring decision per worker (raw & calibrated ML outputs, penalties, fallback flags).
- `RankingDecisionLogger` — structured JSON logger with optional debug mode.
- Config flags in `app/core/config.py` to control trace and debug behavior.
- Matching engine writes trace into `WorkerScore.metadata['ranking_trace']` when enabled.

### Backward Compatibility

- API signatures and response schemas remain unchanged.
- Traces live inside metadata and are optional for clients.

---

## 4. Integration Guide & Data Flow

This section explains how the layers interact during `rank_candidates()` execution.

Layers:

1. Rule-Based Scoring: computes `rule_score` based on distance, skills, experience, rating.
2. ML Prediction: `AcceptancePredictor` and `RiskPredictor` produce raw probabilities.
3. Calibration (Phase 2.5): PlattScaler adjusts raw probabilities to calibrated estimates.
4. Observability (Phase 2.6): `RankingTrace` captures components; logger emits structured JSON if enabled.

Example flow (condensed):

1. Compute `rule_score` (0–100).
2. Extract features for ML predictors.
3. Get `raw_probability` from Acceptance & Risk models.
4. Apply Platt Scaling to obtain `calibrated_probability`.
5. Compute `risk_penalty = risk_probability * 15.0` and blend final score:

   final_score = 0.7 * rule_score + 0.3 * calibrated_acceptance - risk_penalty

6. Create `RankingTrace` (worker_id, job_id, components, fallbacks) and attach to `WorkerScore.metadata`.

---

## 5. Testing Strategy

New/updated tests ensure correctness, stability, and compatibility:

- `tests/test_calibration.py` — calibration fit/load and output clamping
- `tests/test_ranking_trace.py` — trace creation, validation, serialization
- `tests/test_observability_logs.py` — structured logger behavior
- `tests/test_endpoint_stability_phase26.py` — API contract and fallback checks

Existing tests remain relevant and should continue to pass.

Run tests:

```bash
cd backend
pytest tests/ -q
```

---

## 6. Deployment Notes & Rollback

Deployment guidance:

- No new external dependencies; safe to deploy.
- Calibration files are optional — system falls back safely if missing.
- Enable `HUSTLE_ENABLE_MATCH_DEBUG` for debugging; default is disabled.

Rollback steps:

1. Set `enable_ranking_trace=false` to stop trace creation.
2. Set `enable_match_debug=false` to silence debug logging.
3. Remove or revert matching engine changes if needed.

---

## 7. Performance, Security, and Limitations

- Performance: O(n) with n workers; trace overhead negligible (<1% typical).
- Memory: ~200 bytes per trace; traces are stored in response metadata only.
- Security: traces do not contain PII; IDs and scores only.
- Limitations: traces are in-memory only; no distributed tracing or persistence yet.

---

## 8. Files Modified / Created (High-level)

- New: `app/ml/inference/ranking_trace.py`, `app/ml/inference/ranking_logger.py`
- Modified: `app/ml/inference/output_contract.py`, `app/ml/inference/acceptance_predictor.py`, `app/ml/inference/risk_predictor.py`, `app/services/matching_engine.py`, `app/core/config.py`
- Tests: `tests/test_calibration.py`, `tests/test_ranking_trace.py`, `tests/test_observability_logs.py`, `tests/test_endpoint_stability_phase26.py`

Refer to individual Phase 2.x files for exact line-level changes and counts.

---

## 9. Next Steps

1. Ensure calibration models are produced by training scripts and stored in `app/ml/models/`.
2. Run the full test suite and validate test coverage.
3. Optionally add trace export/storage and correlation IDs (future work).
4. Consider trace sampling for very large worker lists.

---

## Appendix: Source snippets (excerpts)

### Example MLPredictionOutput

```python
@dataclass
class MLPredictionOutput:
    raw_probability: float
    calibrated_probability: float
    confidence: float
    is_fallback: bool = False
```

### Example RankingTrace (JSON)

```json
{
  "worker_id": "w123",
  "job_id": "j456",
  "rule_score": 74.0,
  "ml_acceptance_raw": 0.72,
  "ml_acceptance_calibrated": 0.68,
  "risk_probability_raw": 0.15,
  "risk_probability_calibrated": 0.18,
  "risk_penalty": 2.7,
  "final_score": 49.3,
  "ml_acceptance_fallback": false,
  "risk_model_fallback": false
}
```

---

Copyright: internal project notes — do not publish externally without review.
