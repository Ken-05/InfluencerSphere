"""
config.py
---------
Loads environment variables and defines foundational application settings
and constants for the FastAPI service. Uses Pydantic for settings management.
"""
from typing import Optional
from pydantic_settings import BaseSettings, SettingsConfigDict
from functools import lru_cache


class Settings(BaseSettings):
    """
    Application settings loaded from environment variables (e.g., .env file).
    """
    model_config = SettingsConfigDict(
        env_file='.env',
        env_file_encoding='utf-8',
        extra='ignore'
    )

    # --- Core Application Settings ---
    APP_NAME: str = "InfluencerSphere ML API"
    API_V1_STR: str = "/api/v1"

    # --- Firebase/Authentication Settings ---
    FIREBASE_PROJECT_ID: Optional[str] = None
    # JWT secret is typically handled by Firebase Admin SDK, but included for structure
    #AUTH_SECRET_KEY: str = ""

    # --- ML/Model Settings ---
    # Path where model artifacts are expected to be mounted in the container
    MODEL_ARTIFACTS_PATH: str = "/app/models"

    # --- Service/API Limits ---
    DEFAULT_SEARCH_LIMIT: int = 25  # Default number of results for influencer searches
    MAX_API_WORKERS: int = 4  # Limits the concurrency of expensive ML prediction calls

    # --- Alert Management ---
    ALERT_CHECK_INTERVAL_SECONDS: int = 300  # How often the scheduler checks alerts (5 minutes)


@lru_cache()
def get_settings() -> Settings:
    """Provides a cached singleton instance of the application settings."""
    return Settings()
