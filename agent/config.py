"""
Configuration management for the AI agent.
"""
import os
from typing import Dict, Any
from pydantic_settings import BaseSettings
from pydantic import Field
from dotenv import load_dotenv

class Settings(BaseSettings):
    """Application settings loaded from environment variables."""
    openai_api_key: str = Field(..., env="OPENAI_API_KEY")
    openai_model: str = Field("o3-mini", env="OPENAI_MODEL")
    agent4rena_api_key: str = Field(..., env="AGENT4RENA_API_KEY")
    webhook_secret: str = Field(None, env="WEBHOOK_SECRET")
    log_level: str = Field("INFO", env="LOG_LEVEL")
    log_file: str = Field("agent.log", env="LOG_FILE")
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"

def load_config() -> Settings:
    """Load and return application configuration."""
    load_dotenv(override=True)
    return Settings() 