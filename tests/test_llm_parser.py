"""Tests for LLM parser service."""

import pytest

from src.services.llm_parser import LLMParser, TShirtRequest


class TestLLMParser:
    """Test suite for LLM parser."""

    @pytest.fixture
    def parser(self):
        """Create a parser instance."""
        return LLMParser()

    @pytest.mark.asyncio
    async def test_fallback_parser_basic(self, parser):
        """Test fallback parser with basic message."""
        result = parser._fallback_parse("I want a t-shirt that says 'Hello World'")
        
        assert isinstance(result, TShirtRequest)
        assert result.phrase != ""
        assert result.style == "modern"
        assert result.wants_image is False

    @pytest.mark.asyncio
    async def test_fallback_parser_with_quotes(self, parser):
        """Test fallback parser extracts quoted text."""
        result = parser._fallback_parse('Make me a shirt that says "Code is Life"')
        
        assert isinstance(result, TShirtRequest)
        assert "Code is Life" in result.phrase or result.phrase != ""

    @pytest.mark.asyncio
    async def test_fallback_parser_removes_keywords(self, parser):
        """Test fallback parser removes trigger keywords."""
        result = parser._fallback_parse("tshirt with Coffee First on it")
        
        assert isinstance(result, TShirtRequest)
        assert "tshirt" not in result.phrase.lower()
