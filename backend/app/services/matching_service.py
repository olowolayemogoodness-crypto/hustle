from app.ml.scoring import (
    calculate_trust_score,
    calculate_matching_score
)

from app.ml.model import predict_success
from app.ml.explain import generate_explanation


RULE_WEIGHT = 0.65
ML_WEIGHT = 0.35


def match_workers(job, workers):

    results = []

    # Performance optimization
    workers = sorted(
        workers,
        key=lambda w: w["distance_km"]
    )[:50]

    for worker in workers:

        # 1. Trust score
        trust_score = calculate_trust_score(worker)

        # 2. Rule-based matching
        match_score = calculate_matching_score(
            worker["distance_km"],
            worker["skill_overlap"],
            trust_score,
            worker["availability"]
        )

        # 3. Prepare ML features
        features = {
            "distance_km": worker["distance_km"],
            "skill_overlap": worker["skill_overlap"],
            "trust_score": trust_score,
            "rating": worker["rating"],
            "completion_rate": worker["completion_rate"],
            "disputes": worker["disputes"],
            "availability": worker["availability"]
        }

        # 4. ML prediction
        ml_probability = predict_success(features)

        # 5. Blend scores
        final_score = (
            RULE_WEIGHT * match_score +
            ML_WEIGHT * ml_probability
        )

        # 6. Generate explanation
        explanation = generate_explanation(
            worker,
            trust_score
        )

        results.append({
            "worker_id": worker["id"],
            "final_score": round(final_score, 4),
            "trust_score": round(trust_score, 4),
            "ml_probability": round(ml_probability, 4),
            "explanation": explanation
        })

    # 7. Rank workers
    ranked = sorted(
        results,
        key=lambda x: x["final_score"],
        reverse=True
    )

    return ranked