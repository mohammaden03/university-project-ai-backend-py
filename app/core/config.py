from functools import lru_cache
from typing import List, Optional
from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore"
    )

    # General
    APP_NAME: str = "Makhtootat HTR & Research Platform"
    APP_ENV: str = "development"
    DEBUG: bool = True
    PORT: int = 8000
    HOST: str = "0.0.0.0"
    SECRET_KEY: str = "development-secret-key-at-least-32-characters-long"

    # Database
    DATABASE_URL: str = "postgresql+asyncpg://postgres:postgres@localhost:5432/makhtootat_db"
    SYNC_DATABASE_URL: str = "postgresql://postgres:postgres@localhost:5432/makhtootat_db"

    # Redis & Celery
    REDIS_URL: str = "redis://localhost:6379/0"
    CELERY_BROKER_URL: str = "redis://localhost:6379/1"
    CELERY_RESULT_BACKEND: str = "redis://localhost:6379/2"

    # JWT
    JWT_SECRET_KEY: str = "jwt-secret-key-development-minimum-32-chars"
    JWT_ALGORITHM: str = "HS256"
    JWT_ACCESS_TOKEN_EXPIRE_MINUTES: int = 1440
    JWT_REFRESH_TOKEN_EXPIRE_DAYS: int = 7

    # Storage
    STORAGE_BACKEND: str = "local"
    UPLOAD_DIR: str = "./uploads"
    MAX_UPLOAD_SIZE_MB: int = 50
    ALLOWED_IMAGE_EXTENSIONS: str = "jpg,jpeg,png,tiff,tif"

    # S3 / MinIO
    S3_ENDPOINT_URL: Optional[str] = "http://localhost:9000"
    S3_ACCESS_KEY_ID: Optional[str] = "minioadmin"
    S3_SECRET_ACCESS_KEY: Optional[str] = "minioadmin"
    S3_BUCKET_NAME: str = "manuscripts"
    S3_REGION: str = "us-east-1"

    # HTR / OCR
    OCR_DEFAULT_MODEL: str = "trocr_handwritten_persian"
    OCR_MODEL_PATH: str = "./models/htr_checkpoints"
    OCR_DEVICE: str = "cpu"
    OCR_BATCH_SIZE: int = 8
    OCR_MAX_LENGTH: int = 256
    OCR_CONFIDENCE_THRESHOLD: float = 0.65
    ENABLE_IMAGE_PREPROCESSING: bool = True
    ENABLE_LINE_SEGMENTATION: bool = True

    # Embeddings
    EMBEDDING_MODEL_NAME: str = "sentence-transformers/paraphrase-multilingual-mpnet-base-v2"
    EMBEDDING_DIMENSION: int = 768
    EMBEDDING_DEVICE: str = "cpu"
    EMBEDDING_BATCH_SIZE: int = 32
    VECTOR_SEARCH_ENABLED: bool = True
    SEMANTIC_SEARCH_ENABLED: bool = True

    # Text Chunking
    CHUNK_SIZE_WORDS: int = 80
    CHUNK_OVERLAP_WORDS: int = 15

    # LLM / RAG
    LLM_PROVIDER: str = "gemini"
    LLM_API_KEY: Optional[str] = None
    LLM_MODEL: str = "gemini-2.5-flash"
    LLM_BASE_URL: Optional[str] = None
    LLM_TIMEOUT: int = 30
    LLM_MAX_OUTPUT_TOKENS: int = 1024
    LLM_TEMPERATURE: float = 0.2

    # CORS
    CORS_ORIGINS: str = "http://localhost:3000,http://127.0.0.1:3000"

    @property
    def cors_origins_list(self) -> List[str]:
        return [origin.strip() for origin in self.CORS_ORIGINS.split(",") if origin.strip()]

    @property
    def allowed_extensions_set(self) -> set[str]:
        return {ext.strip().lower() for ext in self.ALLOWED_IMAGE_EXTENSIONS.split(",") if ext.strip()}


@lru_cache()
def get_settings() -> Settings:
    return Settings()
