"""
PHASE 2.6 INTEGRATION GUIDE
============================

How Phase 2 (Risk), Phase 2.5 (Calibration), and Phase 2.6 (Observability) 
work together in the matching engine.

ARCHITECTURE LAYERS
===================

Layer 1 - Rule-Based Scoring (Core)
   └─ calculate_simple_score()
      - Distance, skills, experience, rating
      - Returns [0, 100]

Layer 2 - ML Risk Prediction (Phase 2)
   ├─ AcceptancePredictor.predict_probability()
   │  └─ Returns raw ML probability [0, 1]
   └─ RiskPredictor.predict_risk()
      └─ Returns raw risk probability [0, 1]

Layer 3 - Probability Calibration (Phase 2.5)
   ├─ PlattScaler.calibrate()
   │  └─ Adjusts ML probabilities for reliability
   └─ MLPredictionOutput.post_init()
      └─ Clamps calibrated values [0, 1]

Layer 4 - Observability Tracing (Phase 2.6)
   ├─ RankingTrace
   │  └─ Captures all score components
   └─ RankingDecisionLogger
      └─ Logs decisions for debugging

DATA FLOW EXAMPLE
=================

Input: Job (delivery, $100, 5km radius) + 10 workers

rank_candidates() execution:

for worker in workers:
    ┌─ Rule-Based Score
    │  distance_score = 20 (within 5km)
    │  skills_score = 40 (driving match)
    │  experience_score = 4 (2 years)
    │  rating_score = 10 (4.5 rating)
    │  rule_score = 74
    │
    ├─ Extract Features (job + worker metadata)
    │
    ├─ ML Acceptance Prediction
    │  ├─ AcceptancePredictor.predict_probability()
    │  │  └─ Model output: 0.72 (raw)
    │  │
    │  └─ PlattScaler.calibrate()
    │     └─ Adjusted: 0.68 (calibrated)
    │
    ├─ ML Risk Prediction
    │  ├─ RiskPredictor.predict_risk()
    │  │  └─ Model output: 0.15 (raw)
    │  │
    │  └─ PlattScaler.calibrate()
    │     └─ Adjusted: 0.18 (calibrated)
    │
    ├─ Final Score Calculation
    │  │  final_score = (0.7 × rule_score) + (0.3 × ml_acceptance) - risk_penalty
    │  │             = (0.7 × 74) + (0.3 × 0.68) - (0.18 × 15)
    │  │             = 51.8 + 0.204 - 2.7
    │  │             = 49.3
    │
    ├─ Ranking Trace (Phase 2.6)
    │  RankingTrace(
    │    worker_id="w123",
    │    job_id="j456",
    │    rule_score=74.0,
    │    ml_acceptance_raw=0.72,
    │    ml_acceptance_calibrated=0.68,
    │    risk_probability_raw=0.15,
    │    risk_probability_calibrated=0.18,
    │    risk_penalty=2.7,
    │    final_score=49.3,
    │    ml_acceptance_fallback=False,
    │    risk_model_fallback=False
    │  )
    │
    ├─ Structured Logging (if enabled)
    │  {
    │    "event": "ranking_decision",
    │    "job_id": "j456",
    │    "worker_id": "w123",
    │    "scores": {
    │      "rule_score": 74.0,
    │      "ml_acceptance_raw": 0.720,
    │      "ml_acceptance_calibrated": 0.680,
    │      "risk_probability_raw": 0.150,
    │      "risk_probability_calibrated": 0.180,
    │      "risk_penalty": 2.7,
    │      "final_score": 49.3
    │    },
    │    "fallbacks": {
    │      "ml_acceptance": false,
    │      "risk_model": false
    │    },
    │    "passed_threshold": true
    │  }
    │
    └─ Return WorkerScore with trace in metadata

Output: List[WorkerScore] sorted by final_score (descending)
         Each score includes trace in metadata["ranking_trace"]

USAGE EXAMPLES
==============

Example 1: Access trace from ranking result
──────────────────────────────────────────

from app.schemas.job import JobBase
from app.services.matching_engine import rank_candidates

job = JobBase(
    id=1,
    title="Delivery",
    required_skills=["driving"],
    latitude=40.0,
    longitude=-74.0,
    budget=100.0
)

workers = fetch_candidates(job)  # Returns List[WorkerResponse]

ranked = rank_candidates(job, workers)

# Inspect ranking decisions
for score in ranked[:5]:  # Top 5
    worker_id = score.worker_id
    final_score = score.final_score
    
    # Get detailed trace (Phase 2.6)
    trace = score.metadata.get("ranking_trace")
    if trace:
        print(f"Worker {worker_id}:")
        print(f"  Final Score: {final_score}")
        print(f"  Rule Score: {trace['rule_score']}")
        print(f"  ML Acceptance: {trace['ml_acceptance_calibrated']:.3f}")
        print(f"  Risk Probability: {trace['risk_probability_calibrated']:.3f}")
        print(f"  Risk Penalty: {trace['risk_penalty']:.2f}")
        
        # Detect fallbacks
        if trace['ml_acceptance_fallback']:
            print("  ⚠️  Acceptance model not available (using fallback)")
        if trace['risk_model_fallback']:
            print("  ⚠️  Risk model not available (using fallback)")


Example 2: Enable debug logging
───────────────────────────────

# In environment or config:
os.environ['HUSTLE_ENABLE_MATCH_DEBUG'] = 'true'

# Or in FastAPI startup:
from app.core.config import settings
if settings.enable_match_debug:
    logging.getLogger("app.services.matching_engine").setLevel(logging.DEBUG)

# Now rank_candidates will log detailed traces at DEBUG level
ranked = rank_candidates(job, workers)

# Output in logs:
# DEBUG:app.services.matching_engine:Worker w1: rule=50.0, 
#   ml_raw=0.700, ml_cal=0.650, risk_raw=0.150, 
#   risk_cal=0.180, penalty=2.70, final=49.3


Example 3: Analyze score composition
────────────────────────────────────

def analyze_score_composition(score):
    """Understand what drove a worker's score."""
    trace = score.metadata.get("ranking_trace")
    if not trace:
        return None
    
    components = {
        "rule_based": trace['rule_score'] * 0.7,
        "ml_acceptance": trace['ml_acceptance_calibrated'] * 0.3,
        "risk_penalty": -trace['risk_penalty']
    }
    
    print(f"Score breakdown for {score.worker_id}:")
    print(f"  Rule-based contribution: {components['rule_based']:.1f}")
    print(f"  ML acceptance contribution: {components['ml_acceptance']:.1f}")
    print(f"  Risk penalty: {components['risk_penalty']:.1f}")
    print(f"  Final score: {score.final_score:.1f}")
    
    # Identify what dominated the decision
    if abs(components['risk_penalty']) > components['rule_based']:
        print("  → Risk penalty is the limiting factor")
    elif components['rule_based'] > components['ml_acceptance']:
        print("  → Rule-based factors are driving score")
    else:
        print("  → ML acceptance probability is driving score")


Example 4: Monitor model fallbacks
──────────────────────────────────

def monitor_ranking_quality(ranked_workers):
    """Check if ML models are working or in fallback."""
    fallback_count = 0
    total_workers = len(ranked_workers)
    
    for score in ranked_workers:
        trace = score.metadata.get("ranking_trace")
        if trace and (trace['ml_acceptance_fallback'] or trace['risk_model_fallback']):
            fallback_count += 1
    
    fallback_rate = fallback_count / total_workers if total_workers > 0 else 0
    
    print(f"Model health report:")
    print(f"  Total workers ranked: {total_workers}")
    print(f"  Fallback predictions: {fallback_count}")
    print(f"  Fallback rate: {fallback_rate*100:.1f}%")
    
    if fallback_rate > 0.1:  # If >10% fallback
        print("  ⚠️  WARNING: High fallback rate detected!")
        print("     Check if ML models are missing or failing")
    else:
        print("  ✓ Models operating normally")


CONFIGURATION
=============

Environment variables (in .env or system):

HUSTLE_ENABLE_MATCH_DEBUG=false
  → If true, logs full ranking traces at DEBUG level
  → Default: false (no debug output)

HUSTLE_ENABLE_RANKING_TRACE=true
  → If true, captures traces in metadata
  → Default: true (traces always captured)

In Python config:

from app.core.config import settings

enable_debug = settings.enable_match_debug      # bool
enable_trace = settings.enable_ranking_trace    # bool


FALLBACK BEHAVIOR
=================

When ML models are not available (missing .joblib files):

1. AcceptancePredictor returns:
   - raw_probability: 0.5 (neutral)
   - calibrated_probability: 0.5 (neutral)
   - is_fallback: True

2. RiskPredictor returns:
   - raw_probability: 0.0 (no risk)
   - calibrated_probability: 0.0 (no risk)
   - is_fallback: True

3. RankingTrace captures fallback flags:
   - ml_acceptance_fallback: True
   - risk_model_fallback: True

4. Final score uses fallback values:
   - final_score = (0.7 × rule_score) + (0.3 × 0.5) - 0.0
   - Purely rule-based + neutral ML term

5. Client can detect fallback:
   - trace = score.metadata.get("ranking_trace")
   - if trace['ml_acceptance_fallback']: ...


PERFORMANCE CHARACTERISTICS
=============================

Time Complexity: O(n) where n = number of workers
  - One trace created per worker
  - One log entry per worker (if debug enabled)
  - No nested loops or quadratic operations

Space Complexity: O(n)
  - ~200 bytes per trace in metadata
  - ~400 bytes per log entry (JSON)
  - Garbage collected after response

Typical performance:
  - 100 workers: ~50ms (including ML predictions)
  - Trace creation overhead: <1% of total time
  - Debug logging overhead: ~5% (when enabled)


TESTING & VALIDATION
=====================

Test trace structure:
  ✓ test_ranking_trace.py
    - Validates NaN/Inf detection
    - Tests serialization
    - Checks fallback flags

Test logging:
  ✓ test_observability_logs.py
    - Validates JSON structure
    - Tests logger enable/disable
    - Checks component capture

Test backward compatibility:
  ✓ test_endpoint_stability_phase26.py
    - Verifies API contracts unchanged
    - Validates score formats
    - Tests fallback behavior


MONITORING CHECKLIST
====================

In production, monitor:

□ Fallback rates (should be ~0%)
  └─ Alert if > 5% fallback

□ Score distributions
  └─ Alert if distribution shifts

□ Processing time per match
  └─ Alert if > 100ms (with 100 workers)

□ Debug log volume (if enabled)
  └─ Check not exceeding storage limits

□ Calibration performance
  └─ Verify calibrated probs match empirical rates

□ Risk penalty distribution
  └─ Check penalties reasonable


TROUBLESHOOTING
===============

Issue: All workers get fallback predictions
  → Check if .joblib files exist in app/ml/models/
  → Check if model training script was run
  → Check file permissions

Issue: Scores are lower than expected
  → Check if risk_penalty is too high
  → Verify risk model calibration
  → Check if threshold set too high

Issue: Logs growing too large
  → Disable debug logging (set HUSTLE_ENABLE_MATCH_DEBUG=false)
  → Reduce log level to INFO/WARNING

Issue: Performance degradation
  → Profile trace creation time
  → Check logger efficiency
  → Consider worker count limits

END OF INTEGRATION GUIDE
"""
