"""Tests for design generator service."""

import pytest
from pathlib import Path

from src.services.design_generator import DesignGenerator
from src.services.llm_parser import TShirtRequest


class TestDesignGenerator:
    """Test suite for design generator."""

    @pytest.fixture
    def generator(self):
        """Create a generator instance."""
        return DesignGenerator()

    @pytest.mark.asyncio
    async def test_generate_basic_design(self, generator):
        """Test generating a basic text design."""
        request = TShirtRequest(
            phrase="Hello World",
            style="modern",
            wants_image=False,
            image_description=None,
            color_preference=None,
        )
        
        file_path, image_bytes = await generator.generate_design(request)
        
        assert isinstance(file_path, Path)
        assert file_path.exists()
        assert len(image_bytes) > 0
        assert file_path.suffix == ".png"

    @pytest.mark.asyncio
    async def test_generate_design_with_color(self, generator):
        """Test generating a design with color preference."""
        request = TShirtRequest(
            phrase="Test",
            style="modern",
            wants_image=False,
            image_description=None,
            color_preference="blue",
        )
        
        file_path, image_bytes = await generator.generate_design(request)
        
        assert file_path.exists()
        assert len(image_bytes) > 0

    def test_get_text_color_red(self, generator):
        """Test color mapping for red."""
        color = generator._get_text_color("red")
        assert color == (255, 0, 0, 255)

    def test_get_text_color_default(self, generator):
        """Test default color when no preference."""
        color = generator._get_text_color(None)
        assert color == (0, 0, 0, 255)  # Black

    def test_get_outline_color_dark_text(self, generator):
        """Test outline color for dark text."""
        outline = generator._get_outline_color((0, 0, 0, 255))
        assert outline == (255, 255, 255, 255)  # White outline

    def test_get_outline_color_light_text(self, generator):
        """Test outline color for light text."""
        outline = generator._get_outline_color((255, 255, 255, 255))
        assert outline == (0, 0, 0, 255)  # Black outline
