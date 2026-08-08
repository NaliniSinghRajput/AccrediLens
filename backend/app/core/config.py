from functools import lru_cache
from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "AccrediLens"
    environment: str = "development"

    database_url: str = "postgresql+psycopg2://lms:lms_password@localhost:5432/intelligent_lms"
    redis_url: str = "redis://localhost:6379/0"
    qdrant_url: str = "http://localhost:6333"
    qdrant_collection: str = "paper_chunks"

    ollama_base_url: str = "http://localhost:11434"
    llm_model: str = "qwen3:8b"
    fast_llm_model: str = "qwen3:4b"
    embedding_model: str = "nomic-embed-text"

    jwt_secret_key: str = "change-this-local-secret"
    jwt_algorithm: str = "HS256"
    access_token_expire_minutes: int = 60 * 24

    upload_dir: Path = Path("storage/uploads")
    process_inline: bool = False
    retrieval_top_k: int = 12
    final_context_k: int = 5
    similarity_threshold: float = 0.32
    sufficiency_min_sources: int = 1

    frontend_origin: str = "http://localhost:3001"

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")


@lru_cache
def get_settings() -> Settings:
    settings = Settings()
    settings.upload_dir.mkdir(parents=True, exist_ok=True)
    return settings
