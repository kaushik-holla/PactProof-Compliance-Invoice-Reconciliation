"""
App config and env settings
"""

import os
from pathlib import Path
from functools import lru_cache
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    
    app_mode: str = "ADE"
    api_origin: str = "http://localhost:8000"
    vision_agent_api_key: str = ""
    google_api_key: str = ""
    vite_api_base_url: str = "http://localhost:8000"
    max_upload_size_mb: int = 50
    upload_dir: str = "uploads"
    fuzzy_match_threshold: int = 85
    allowed_variance_pct: float = 2.0
    
    class Config:
        env_file = str(Path(__file__).parent.parent / ".env")
        case_sensitive = False


@lru_cache()
def get_settings() -> Settings:
    return Settings()

