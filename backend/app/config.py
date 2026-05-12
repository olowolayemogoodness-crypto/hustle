from pathlib import Path
from typing import List

from pydantic_settings import BaseSettings, SettingsConfigDict

BASE_DIR = Path(__file__).resolve().parent
DOTENV_PATH = BASE_DIR.parent / ".env"

class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_prefix="HUSTLE_",
        env_file=str(DOTENV_PATH),
        env_file_encoding="utf-8",
    )

    app_name: str = "Hustle Backend"
    app_version: str = "1.0.0"
    model_relative_path: str = "../scripts/model.joblib"
    logging_level: str = "INFO"
    debug: bool = False
    api_prefix: str = "/api/v1"
    host: str = "0.0.0.0"
    port: int = 8000
    max_workers_evaluated: int = 50
    rule_weight: float = 0.65
    ml_weight: float = 0.35
    fallback_probability: float = 0.5
    match_threshold: float = 0.0
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
