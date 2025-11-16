"""Pytest configuration and shared fixtures."""

import os
import pytest
from pathlib import Path


def pytest_configure(config):
    """Set up test environment variables before any tests run."""
    os.environ["DISCORD_BOT_TOKEN"] = "test_discord_token"
    os.environ["GOOGLE_API_KEY"] = "test_google_key"
    os.environ["PRINTFUL_API_KEY"] = "test_printful_key"
    os.environ["PRINTFUL_STORE_ID"] = "test_store_id"
    os.environ["LANGCHAIN_API_KEY"] = "test_langchain_key"
    os.environ["LANGCHAIN_TRACING_V2"] = "false"
    os.environ["BOT_LOG_LEVEL"] = "ERROR"


@pytest.fixture
def temp_image_dir(tmp_path):
    """Create a temporary directory for test images."""
    image_dir = tmp_path / "test_images"
    image_dir.mkdir()
    return image_dir


@pytest.fixture(autouse=True)
def cleanup_generated_images():
    """Clean up generated test images after each test."""
    yield
    # Cleanup after test
    test_image_dir = Path("generated_images")
    if test_image_dir.exists():
        for file in test_image_dir.glob("design_*.png"):
            if file.name.startswith("design_-"):  # Test images only
                file.unlink()
