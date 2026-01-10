"""
Configuration Management for SafeGuard AI Backend

Handles all environment variables and configuration settings
"""

from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    """Application settings loaded from environment variables"""

    # Application
    APP_NAME: str = "SafeGuard AI Backend"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = False

    # Server
    HOST: str = "0.0.0.0"
    PORT: int = 8000
    FRONTEND_URL: str = "http://localhost:3000"

    # Database
    DATABASE_URL: str

    # AI API Keys
    ANTHROPIC_API_KEY: str
    OPENAI_API_KEY: str

    # Email Configuration
    SMTP_HOST: str = "smtp.gmail.com"
    SMTP_PORT: int = 587
    SMTP_USER: Optional[str] = None
    SMTP_PASSWORD: Optional[str] = None
    SMTP_FROM_EMAIL: Optional[str] = None

    # Redis
    REDIS_URL: str = "redis://localhost:6379"

    # Model Paths
    YOLO_WEIGHTS: str = "./weights/yolov8n.pt"
    ACTION_WEIGHTS: Optional[str] = "./weights/timesformer_quantized.pth"
    FIRE_WEIGHTS: Optional[str] = "./weights/weather_resnet18.pth"

    # Security
    ENCRYPTION_KEY: str  # For encrypting camera passwords

    # Rate Limiting
    RATE_LIMIT_PER_MINUTE: int = 60

    class Config:
        env_file = ".env"
        case_sensitive = True


# Global settings instance
settings = Settings()
