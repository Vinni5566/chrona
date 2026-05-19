import logging
from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import Optional
from dotenv import load_dotenv

# Ensure dotenv is loaded if pydantic_settings misses it from root
load_dotenv()

class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file='.env',
        env_file_encoding='utf-8',
        extra='ignore'
    )

    # Hindsight
    HINDSIGHT_API_KEY: Optional[str] = None
    HINDSIGHT_PROJECT_ID: Optional[str] = None
    HINDSIGHT_BASE_URL: Optional[str] = None

    # Storage
    CHRONA_STORAGE_MODE: str = "local"
    CHRONA_DATA_DIR: str = "./data"

    # Vector Store
    VECTOR_STORE_PROVIDER: str = "local"

    # LLM Providers
    OPENAI_API_KEY: Optional[str] = None
    GROQ_API_KEY: Optional[str] = None
    ANTHROPIC_API_KEY: Optional[str] = None
    OLLAMA_BASE_URL: str = "http://localhost:11434"

    # cascadeflow
    CASCADEFLOW_ENABLED: bool = True
    CASCADEFLOW_DEFAULT_MODEL: str = "qwen/qwen3-32b"
    CASCADEFLOW_FALLBACK_MODEL: str = "openai/gpt-oss-120b"

    # Runtime Controls
    CHRONA_MAX_CONTEXT_TOKENS: int = 12000
    CHRONA_MAX_FILE_SIZE_MB: int = 5
    CHRONA_ENABLE_SANITIZATION: bool = True
    CHRONA_ENABLE_AUDIT_LOGS: bool = True

    # Security
    CHRONA_MASK_SECRETS: bool = True
    CHRONA_DISABLE_RAW_LOG_EXPORT: bool = True

    # Debug
    CHRONA_DEBUG: bool = True

    def validate_providers(self):
        if self.CHRONA_STORAGE_MODE == "hindsight":
            if not self.HINDSIGHT_API_KEY or not self.HINDSIGHT_PROJECT_ID:
                logging.warning("Hindsight storage mode is set, but API Key/Project ID are missing. Falling back to local.")
                self.CHRONA_STORAGE_MODE = "local"

settings = Settings()
settings.validate_providers()
