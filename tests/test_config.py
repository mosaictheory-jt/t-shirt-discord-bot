"""Tests for configuration module."""

import os
import pytest

from src.config import Settings


class TestSettings:
    """Test suite for settings."""

    def test_trigger_keywords_list(self):
        """Test parsing trigger keywords into list."""
        settings = Settings(
            discord_bot_token="test_token",
            google_api_key="test_key",
            printful_api_key="test_key",
            bot_trigger_keywords="tshirt,shirt,merch",
        )
        
        keywords = settings.trigger_keywords_list
        assert len(keywords) == 3
        assert "tshirt" in keywords
        assert "shirt" in keywords
        assert "merch" in keywords

    def test_guild_ids_list_empty(self):
        """Test parsing empty guild IDs."""
        settings = Settings(
            discord_bot_token="test_token",
            google_api_key="test_key",
            printful_api_key="test_key",
            discord_guild_ids="",
        )
        
        guild_ids = settings.guild_ids_list
        assert len(guild_ids) == 0

    def test_guild_ids_list_with_values(self):
        """Test parsing guild IDs with values."""
        settings = Settings(
            discord_bot_token="test_token",
            google_api_key="test_key",
            printful_api_key="test_key",
            discord_guild_ids="123456789,987654321",
        )
        
        guild_ids = settings.guild_ids_list
        assert len(guild_ids) == 2
        assert 123456789 in guild_ids
        assert 987654321 in guild_ids
