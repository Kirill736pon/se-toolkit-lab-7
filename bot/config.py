"""
Bot configuration loaded from environment variables.

Reads secrets from .env.bot.secret file.
"""

from pathlib import Path

from pydantic_settings import BaseSettings

# Find .env.bot.secret in the project root (parent of bot/)
BASE_DIR = Path(__file__).parent.parent
ENV_FILE = BASE_DIR / ".env.bot.secret"


class BotSettings(BaseSettings):
    """Bot settings from environment variables."""

    bot_token: str
    lms_api_url: str
    lms_api_key: str
    llm_api_key: str
    llm_api_base_url: str
    llm_api_model: str

    class Config:
        env_file = ENV_FILE
        env_file_encoding = "utf-8"


# Global settings instance
settings = BotSettings()
