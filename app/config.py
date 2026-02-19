"""
Application configuration using Pydantic Settings
"""

from functools import lru_cache
from typing import List, Optional

from pydantic import Field, PostgresDsn, RedisDsn, validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings"""
    
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=True,
    )
    
    # Environment
    ENVIRONMENT: str = Field(default="development", pattern="^(development|staging|production)$")
    DEBUG: bool = Field(default=False)
    SECRET_KEY: str = Field(...)
    
    # API
    API_HOST: str = Field(default="0.0.0.0")
    API_PORT: int = Field(default=8000)
    API_WORKERS: int = Field(default=4)
    
    # CORS
    CORS_ORIGINS: List[str] = Field(default=["http://localhost:8501", "http://localhost:3000"])
    
    @validator("CORS_ORIGINS", pre=True)
    def parse_cors_origins(cls, v):
        if isinstance(v, str):
            return [origin.strip() for origin in v.split(",")]
        return v
    
    # Database
    DATABASE_URL: PostgresDsn = Field(...)
    DATABASE_POOL_SIZE: int = Field(default=20)
    DATABASE_MAX_OVERFLOW: int = Field(default=30)
    
    SQLITE_URL: Optional[str] = Field(default=None)
    SQLITE_WAL_MODE: bool = Field(default=True)
    
    # Redis
    REDIS_URL: RedisDsn = Field(...)
    REDIS_POOL_SIZE: int = Field(default=50)
    
    # Celery
    CELERY_BROKER_URL: str = Field(...)
    CELERY_RESULT_BACKEND: str = Field(...)
    
    # Security
    JWT_SECRET_KEY: str = Field(...)
    JWT_ALGORITHM: str = Field(default="HS256")
    ACCESS_TOKEN_EXPIRE_MINUTES: int = Field(default=30)
    REFRESH_TOKEN_EXPIRE_DAYS: int = Field(default=7)
    BCRYPT_ROUNDS: int = Field(default=12)
    
    # External APIs
    ALPHA_VANTAGE_API_KEY: Optional[str] = Field(default=None)
    YAHOO_FINANCE_ENABLED: bool = Field(default=True)
    
    # ML / NLP
    MODEL_CACHE_DIR: str = Field(default="./models")
    FINBERT_MODEL: str = Field(default="ProsusAI/finbert")
    BERTIMBAU_MODEL: str = Field(default="neuralmind/bert-base-portuguese-cased")
    
    # Feature Flags
    ENABLE_ML_PREDICTIONS: bool = Field(default=True)
    ENABLE_NLP_SENTIMENT: bool = Field(default=True)
    ENABLE_REALTIME_WEBSOCKET: bool = Field(default=True)
    ENABLE_FUNDAMENTAL_ANALYSIS: bool = Field(default=True)
    
    @property
    def is_production(self) -> bool:
        return self.ENVIRONMENT == "production"
    
    @property
    def is_development(self) -> bool:
        return self.ENVIRONMENT == "development"


@lru_cache()
def get_settings() -> Settings:
    """Cached settings instance"""
    return Settings()


settings = get_settings()
