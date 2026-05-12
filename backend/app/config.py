from pathlib import Path
from typing import List

from pydantic import field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


BASE_DIR = Path(__file__).resolve().parent
ROOT_DIR = BASE_DIR.parent
DOTENV_PATH = ROOT_DIR / ".env"


class Settings(BaseSettings):
    """
    Central application configuration.
    Loaded automatically from .env using HUSTLE_ prefix.
    """

    model_config = SettingsConfigDict(
        env_prefix="HUSTLE_",
        env_file=str(DOTENV_PATH),
        env_file_encoding="utf-8",
        extra="ignore",
    )

    # =========================================================
    # APP
    # =========================================================
    app_name: str = "Hustle Backend"
    app_version: str = "1.0.0"

    environment: str = "development"
    debug: bool = False

    host: str = "0.0.0.0"
    port: int = 8000

    api_prefix: str = "/api/v1"

    # =========================================================
    # DATABASE
    # =========================================================
    database_url: str = ""

    # =========================================================
    # SECURITY / JWT
    # =========================================================
    jwt_secret: str = "change_me"
    jwt_expire_minutes: int = 10080  # 7 days

    # =========================================================
    # TERMII SMS
    # =========================================================
    termii_api_key: str = ""
    termii_sender_id: str = "LocGig"

    # =========================================================
    # LOGGING
    # =========================================================
    logging_level: str = "INFO"

    # =========================================================
    # ML MODEL
    # =========================================================
    model_relative_path: str = "../scripts/model.joblib"

    rule_weight: float = 0.65
    ml_weight: float = 0.35

    fallback_probability: float = 0.5
    match_threshold: float = 0.0

    max_workers_evaluated: int = 50

    # =========================================================
    # FEATURE ENGINEERING
    # =========================================================
    feature_columns: List[str] = [
        "distance_km",
        "skill_overlap",
        "trust_score",
        "rating",
        "completion_rate",
        "disputes",
        "availability",
    ]

    # =========================================================
    # CORS
    # =========================================================
    allowed_origins: List[str] = [
        "http://localhost:3000",
        "http://127.0.0.1:3000",
    ]

    # =========================================================
    # COMPUTED PATHS
    # =========================================================
    @property
    def model_path(self) -> str:
        return str((BASE_DIR / self.model_relative_path).resolve())

    # =========================================================
    # VALIDATORS
    # =========================================================
    @field_validator("environment")
    @classmethod
    def validate_environment(cls, v: str) -> str:
        allowed = {"development", "staging", "production"}
        if v not in allowed:
            raise ValueError(
                f"environment must be one of {allowed}"
            )
        return v

    @field_validator("rule_weight")
    @classmethod
    def validate_rule_weight(cls, v: float) -> float:
        if not 0 <= v <= 1:
            raise ValueError("rule_weight must be between 0 and 1")
        return v

    @field_validator("ml_weight")
    @classmethod
    def validate_ml_weight(cls, v: float) -> float:
        if not 0 <= v <= 1:
            raise ValueError("ml_weight must be between 0 and 1")
        return v

    @property
    def total_weight(self) -> float:
        return self.rule_weight + self.ml_weight

    @property
    def is_production(self) -> bool:
        return self.environment == "production"


settings = Settings()