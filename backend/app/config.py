from pathlib import Path
from typing import List

BASE_DIR = Path(__file__).resolve().parent

class Settings:
    app_name: str = "Hustle Backend"
    app_version: str = "1.0.0"
    model_relative_path: str = "../scripts/model.joblib"
    logging_level: str = "INFO"
    debug: bool = False
    max_workers_evaluated: int = 50
    rule_weight: float = 0.65
    ml_weight: float = 0.35
    fallback_probability: float = 0.5
    feature_columns: List[str] = [
        "distance_km",
        "skill_overlap",
        "trust_score",
        "rating",
        "completion_rate",
        "disputes",
        "availability",
    ]

    @property
    def model_path(self) -> str:
        return str((BASE_DIR / self.model_relative_path).resolve())

settings = Settings()
