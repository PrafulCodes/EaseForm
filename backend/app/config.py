"""
Configuration module for EaseForm backend.
Loads environment variables and provides app settings.
"""

from pydantic_settings import BaseSettings
from functools import lru_cache


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""
    
    # Supabase
    supabase_url: str
    supabase_anon_key: str
    supabase_service_key: str
    
    # Frontend
    frontend_url: str = "http://localhost:8080"
    
    # Environment
    environment: str = "development"
    
    # API
    api_prefix: str = "/api"
    
    class Config:
        env_file = ".env"
        case_sensitive = False


@lru_cache()
def get_settings() -> Settings:
    """Get cached settings instance."""
    return Settings()
