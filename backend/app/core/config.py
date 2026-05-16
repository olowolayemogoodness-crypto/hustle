from pathlib import Path
from typing import Literal

from pydantic import Field, computed_field
from pydantic_settings import BaseSettings, SettingsConfigDict


BASE_DIR = Path(__file__).resolve().parent
ROOT_DIR = BASE_DIR.parent.parent
DOTENV_PATH = ROOT_DIR / ".env"

class Settings(BaseSettings):
    squad_base_url: str = "https://sandbox-api-d.squadco.com"
    squad_secret_key: str = ""
    squad_webhook_secret: str = ""

    """
    Centralized application settings.
    Automatically loaded from .env with HUSTLE_ prefix.
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

    environment: Literal[
        "development",
        "staging",
        "production",
    ] = "development"

    debug: bool = False
    testing: bool = False

    host: str = "0.0.0.0"
    port: int = 8000
    fallback_probability: float = 0.5

    api_prefix: str = "/api/v1"

    # =========================================================
    # SUPABASE
    # =========================================================
    supabase_url: str = ""
    supabase_anon_key: str = ""
    supabase_service_role_key: str = ""

    # =========================================================
    # DATABASE POOL
    # =========================================================
    db_pool_size: int = 20
    db_max_overflow: int = 10
    db_pool_timeout: int = 30
    db_pool_recycle: int = 1800

    # =========================================================
    # SECURITY
    # =========================================================
    access_token_expire_minutes: int = 60
    refresh_token_expire_days: int = 30

    # =========================================================
    # RATE LIMITING
    # =========================================================
    rate_limit_per_minute: int = 60

    # =========================================================
    # OTP
    # =========================================================
    otp_expiry_minutes: int = 5
    otp_max_attempts: int = 3

    # =========================================================
    # DATABASE
    # =========================================================
    database_url: str = Field(
        default="",
        description="Async PostgreSQL connection string",
    )

    # =========================================================
    # SECURITY / JWT
    # =========================================================
    jwt_secret: str = Field(
        default="change_me",
        min_length=16,
    )

    jwt_expire_minutes: int = Field(
        default=10080,
        gt=0,
    )

    # =========================================================
    # TERMII SMS
    # =========================================================
    termii_api_key: str = ""
    termii_sender_id: str = "Hustle"

    # =========================================================
    # LOGGING
    # =========================================================
    fallback_probability: float = 0.5

    logging_level: Literal[
        "DEBUG",
        "INFO",
        "WARNING",
        "ERROR",
        "CRITICAL",
    ] = "INFO"

    # =========================================================
    # CORS
    # =========================================================
    allowed_origins: list[str] = [
        "http://localhost:3000",
        "http://127.0.0.1:3000",
    ]

    # =========================================================
    # COMPUTED PROPERTIES
    # =========================================================
    @computed_field
    @property
    def is_production(self) -> bool:
        return self.environment == "production"

    @computed_field
    @property
    def is_development(self) -> bool:
        return self.environment == "development"


settings = Settings()
squad_secret_key:     str = ""
squad_webhook_secret: str = ""
squad_base_url:       str = "https://sandbox-api-d.squadco.com"
# add inside Settings class before computed properties

    # =========================================================
    # SQUAD
    # =========================================================
    