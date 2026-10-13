from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import Field
from pathlib import Path
import os

BASE_DIR = Path(__file__).resolve().parent.parent.parent

class Settings(BaseSettings):
    app_name: str = "LinkedIn B2B Growth & Sales Copilot"
    app_env: str = "production"
    debug: bool = False
    
    # Storage
    database_path: str = str(BASE_DIR / "linkedin_copilot.db")
    backup_dir: str = str(BASE_DIR / "backups")
    uploads_dir: str = str(BASE_DIR / "uploads")
    
    # DeepSeek Configuration
    deepseek_api_key: str = Field(default="", validation_alias="DEEPSEEK_API_KEY")
    deepseek_base_url: str = Field(default="https://api.deepseek.com", validation_alias="DEEPSEEK_BASE_URL")
    deepseek_model: str = Field(default="deepseek-chat", validation_alias="DEEPSEEK_MODEL")
    deepseek_timeout_seconds: float = 60.0
    deepseek_max_retries: int = 2
    
    # DeepSeek Pricing per million tokens (USD)
    # Cache hit input: $0.14/1M, Cache miss input: $0.28/1M, Output: $2.19/1M
    cost_per_1m_input_cache_miss: float = 0.28
    cost_per_1m_input_cache_hit: float = 0.14
    cost_per_1m_output: float = 2.19
    
    model_config = SettingsConfigDict(
        env_file=str(BASE_DIR / ".env"),
        env_file_encoding="utf-8",
        extra="ignore"
    )

    @property
    def is_api_key_configured(self) -> bool:
        return bool(self.deepseek_api_key and self.deepseek_api_key.strip())

settings = Settings()
