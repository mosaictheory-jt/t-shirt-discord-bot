"""Configuration management for the Discord T-Shirt Bot."""

import logging
from typing import List

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
    )

    # Discord Configuration
    discord_bot_token: str = Field(..., description="Discord bot token")
    discord_guild_ids: str = Field(
        default="",
        description="Comma-separated list of guild IDs to monitor",
    )

    # Google Gemini API
    google_api_key: str = Field(..., description="Google API key for Gemini")

    # Langsmith Configuration
    langchain_api_key: str = Field(
        default="",
        description="Langsmith API key for tracing",
    )
    langchain_tracing_v2: bool = Field(
        default=True,
        description="Enable Langsmith tracing",
    )
    langchain_project: str = Field(
        default="discord-tshirt-bot",
        description="Langsmith project name",
    )

    # Printify API
    printify_api_key: str = Field(..., description="Printify API key")
    printify_shop_id: str = Field(..., description="Printify shop ID")

    # Bot Configuration
    bot_trigger_keywords: str = Field(
        default="tshirt,t-shirt,shirt,merch",
        description="Comma-separated list of trigger keywords",
    )
    bot_log_level: str = Field(
        default="INFO",
        description="Logging level",
    )

    @property
    def trigger_keywords_list(self) -> List[str]:
        """Get trigger keywords as a list."""
        return [k.strip().lower() for k in self.bot_trigger_keywords.split(",")]

    @property
    def guild_ids_list(self) -> List[int]:
        """Get guild IDs as a list of integers."""
        if not self.discord_guild_ids:
            return []
        return [int(g.strip()) for g in self.discord_guild_ids.split(",") if g.strip()]

    def setup_logging(self) -> None:
        """Set up logging configuration."""
        logging.basicConfig(
            level=getattr(logging, self.bot_log_level.upper()),
            format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
            handlers=[
                logging.StreamHandler(),
                logging.FileHandler("bot.log"),
            ],
        )


# Global settings instance
settings = Settings()
