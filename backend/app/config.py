"""
Configuration settings for AgroArc Backend
Load environment variables and app settings
"""

from pydantic_settings import BaseSettings, SettingsConfigDict
from functools import lru_cache
import os
from pathlib import Path

BACKEND_DIR = Path(__file__).resolve().parent.parent
ENV_FILE = BACKEND_DIR / ".env"


class Settings(BaseSettings):
    """
    Application settings loaded from environment variables
    """
    
    # API Configuration
    API_TITLE: str = "AgroArc API"
    API_DESCRIPTION: str = "Smart Farmer Support System - ML-based crop and fertilizer recommendations"
    API_VERSION: str = "1.0.0"
    
    # Environment
    ENVIRONMENT: str = os.getenv("ENVIRONMENT", "development")
    DEBUG: bool = (
        os.getenv(
            "DEBUG",
            "false" if os.getenv("ENVIRONMENT", "development") == "production" else "true",
        ).lower()
        == "true"
    )
    
    # API Keys
    OPENWEATHER_API_KEY: str = os.getenv("OPENWEATHER_API_KEY", "")
    
    # Database (optional for future use)
    DATABASE_URL: str = os.getenv("DATABASE_URL", "sqlite:///agroarc.db")
    
    # Paths
    BASE_DIR: Path = Path(__file__).parent.parent.parent
    MODELS_DIR: Path = BASE_DIR / "models"
    
    # CORS
    ALLOWED_ORIGINS: list = [
        "http://localhost",
        "http://localhost:3000",
        "http://localhost:5173",
        "http://127.0.0.1",
        "http://127.0.0.1:3000",
    ]

    model_config = SettingsConfigDict(
        env_file=str(ENV_FILE),
        case_sensitive=True,
        extra="ignore",
    )


@lru_cache()
def get_settings() -> Settings:
    """
    Cached settings instance
    Used to avoid reloading environment variables
    """
    return Settings()
