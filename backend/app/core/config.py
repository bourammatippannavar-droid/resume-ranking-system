from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
	DATABASE_URL: str
	EMBEDDING_DEVICE: str = "cpu"
	EMBEDDING_MODEL_NAME: str = "all-MiniLM-L6-v2"
	VECTOR_BACKEND: str = "faiss"
	LOG_LEVEL: str = "INFO"

	model_config = SettingsConfigDict(
		env_file=".env",
		env_file_encoding="utf-8",
		extra="ignore",
	)


@lru_cache
def get_settings() -> Settings:
	return Settings()
