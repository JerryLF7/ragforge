import logging

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env")

    anthropic_api_key: str = ""
    voyage_api_key: str = ""
    claude_model: str = "claude-sonnet-4-20250514"
    voyage_embedding_model: str = "voyage-3"
    embedding_dimensions: int = 1024
    chunk_size: int = Field(default=1000, gt=0, le=10000)
    chunk_overlap: int = Field(default=200, ge=0, le=5000)
    chroma_path: str = "./data/chroma"
    upload_dir: str = "./uploads"
    top_k: int = Field(default=5, gt=0, le=100)
    rrf_k: int = Field(default=60, gt=0)
    max_upload_size_mb: int = Field(default=50, gt=0, le=500)


settings = Settings()
