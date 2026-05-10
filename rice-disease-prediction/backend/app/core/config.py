"""
Rice Disease Prediction API — Core Configuration

Reads all settings from environment variables / .env file.
"""

from pydantic_settings import BaseSettings
from typing import List


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    # ─── Database ───
    DATABASE_URL: str = "postgresql://riceuser:ricepass123@db:5432/rice_disease"

    # ─── Authentication ───
    SECRET_KEY: str = "change-this-to-a-long-random-string-in-production"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 1440  # 24 hours

    # ─── Storage ───
    STORAGE_TYPE: str = "local"  # "local" or "s3"
    AWS_ACCESS_KEY_ID: str = ""
    AWS_SECRET_ACCESS_KEY: str = ""
    S3_BUCKET_NAME: str = "rice-disease-images"
    AWS_REGION: str = "us-east-1"
    UPLOAD_DIR: str = "./uploads"

    # ─── Redis ───
    REDIS_URL: str = "redis://redis:6379/0"

    # ─── ML Model ───
    MODEL_PATH: str = "./ml/model/efficientnet_rice.pth"

    # ─── App ───
    ENVIRONMENT: str = "development"
    CORS_ORIGINS: str = "http://localhost:3000,http://localhost:5173,http://localhost:80"

    @property
    def cors_origins_list(self) -> List[str]:
        return [origin.strip() for origin in self.CORS_ORIGINS.split(",")]

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = True


settings = Settings()
