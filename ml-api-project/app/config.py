# app/config.py
from functools import lru_cache
from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    # API Configurations
    API_TITLE: str = "California Housing ML Service"
    API_VERSION: str = "1.0.0"
    API_DESCRIPTION: str = "Production-ready FastAPI service for housing valuations with versioned API routes."
    
    # Model & File Paths
    MODEL_PATH: str = "ml/saved_model/model.joblib"
    METADATA_PATH: str = "ml/saved_model/metadata.json"
    LOG_FILE_PATH: str = "logs/app.log"
    
    # Operational Limits & Logging
    LOG_LEVEL: str = "INFO"
    MAX_BATCH_SIZE: int = 100

    # Pydantic Settings configuration to load values from a .env file
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore"
    )

@lru_cache()
def get_settings() -> Settings:
    """Returns a cached instance of Settings to avoid re-reading disk on every call."""
    return Settings()

settings = get_settings()