from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    openai_api_key: str = ""
    openai_chat_model: str = "gpt-4o-mini"
    openai_embedding_model: str = "text-embedding-3-small"
    embedding_dimensions: int = 1536
    chunk_size: int = 1000
    chunk_overlap: int = 200
    chroma_path: str = "./data/chroma"
    upload_dir: str = "./uploads"
    top_k: int = 5

    class Config:
        env_file = ".env"


settings = Settings()
