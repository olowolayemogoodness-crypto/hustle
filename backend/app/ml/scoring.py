def calculate_trust_score(worker):
    score = (
        0.4 * worker["completion_rate"] +
        0.3 * (worker["rating"] / 5) +
        0.2 * (1 - min(worker["disputes"] / 10, 1)) +
        0.1 * worker["availability"]
    )

    return round(score, 4)


def calculate_matching_score(
    distance_km,
    skill_overlap,
    trust_score,
    availability
):
    distance_score = max(0, 1 - (distance_km / 20))

    score = (
        0.3 * distance_score +
        0.3 * skill_overlap +
        0.3 * trust_score +
        0.1 * availability
    )

    return round(score, 4)