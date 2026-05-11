def generate_explanation(worker, trust_score):
    reasons = []

    if trust_score > 0.75:
        reasons.append("High trust score")

    if worker["distance_km"] < 5:
        reasons.append("Very close to job")

    if worker["skill_overlap"] > 0.7:
        reasons.append("Strong skill match")

    if worker["completion_rate"] > 0.85:
        reasons.append("Excellent completion history")

    return reasons[:3]