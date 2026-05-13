from typing import Any, Dict, List


def rank_workers(results: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    ranked = sorted(
        results,
        key=lambda item: (
            item.get("final_score", 0.0),
            item.get("confidence", 0.0),
            item.get("trust_score", 0.0),
            item.get("ml_probability", 0.0),
        ),
        reverse=True,
    )

    for position, row in enumerate(ranked, start=1):
        row["rank"] = position
    return ranked
