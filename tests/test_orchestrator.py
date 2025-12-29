"""Tests for orchestrator service."""

import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from pathlib import Path

from src.services.orchestrator import TShirtOrchestrator, TShirtResult
from src.services.llm_parser import TShirtRequest
from src.services.printify_client import PrintifyProduct


class TestTShirtOrchestrator:
    """Test suite for TShirtOrchestrator."""

    @pytest.fixture
    def orchestrator(self):
        """Create an orchestrator instance."""
        return TShirtOrchestrator()

    @pytest.fixture
    def sample_request(self):
        """Create a sample TShirtRequest."""
        return TShirtRequest(
            phrase="Hello World",
            style="modern",
            wants_image=False,
            image_description=None,
            color_preference="black",
        )

    @pytest.fixture
    def sample_product(self):
        """Create a sample PrintifyProduct."""
        return PrintifyProduct(
            product_id="prod_456",
            title="Test Product",
            description="Custom design",
            blueprint_id=5,
            print_provider_id=99,
            variant_id=101,
            external_id="test_123",
            thumbnail_url="https://example.com/thumb.jpg",
            retail_price=29.99,
            currency="USD",
            product_url="https://printify.com/app/products/prod_456",
            publish_status="unpublished",
        )

    @pytest.mark.asyncio
    async def test_initialize(self, orchestrator):
        """Test orchestrator initialization."""
        with patch.object(orchestrator.printify_client, 'initialize', new_callable=AsyncMock) as mock_init:
            await orchestrator.initialize()
            mock_init.assert_called_once()

    @pytest.mark.asyncio
    async def test_cleanup(self, orchestrator):
        """Test orchestrator cleanup."""
        with patch.object(orchestrator.printify_client, 'cleanup', new_callable=AsyncMock) as mock_cleanup:
            await orchestrator.cleanup()
            mock_cleanup.assert_called_once()

    @pytest.mark.asyncio
    async def test_process_tshirt_request_success(
        self,
        orchestrator,
        sample_request,
        sample_product,
    ):
        """Test successful t-shirt request processing."""
        # Mock the parser
        with patch.object(
            orchestrator.llm_parser,
            'parse_message',
            new_callable=AsyncMock,
            return_value=sample_request,
        ):
            # Mock the design generator
            with patch.object(
                orchestrator.design_generator,
                'generate_design',
                new_callable=AsyncMock,
                return_value=(Path("/tmp/test.png"), b"fake_image_data"),
            ):
                # Mock the Printify client
                with patch.object(
                    orchestrator.printify_client,
                    'create_product',
                    new_callable=AsyncMock,
                    return_value=sample_product,
                ):
                    result = await orchestrator.process_tshirt_request(
                        message="I want a shirt that says 'Hello World'",
                        user_id="test_user_123",
                        username="TestUser",
                    )

        assert result.success is True
        assert result.product_url is not None
        assert "order_12345" in result.product_url
        assert result.response_phrase in TShirtOrchestrator.RESPONSE_PHRASES
        assert result.phrase == "Hello World"
        assert result.error_message is None

    @pytest.mark.asyncio
    async def test_process_tshirt_request_parse_failure(self, orchestrator):
        """Test request processing when parser returns None."""
        with patch.object(
            orchestrator.llm_parser,
            'parse_message',
            new_callable=AsyncMock,
            return_value=None,
        ):
            result = await orchestrator.process_tshirt_request(
                message="invalid message",
                user_id="test_user",
                username="TestUser",
            )

        assert result.success is False
        assert result.error_message == "Failed to parse message"
        assert result.product_url is None

    @pytest.mark.asyncio
    async def test_process_tshirt_request_design_failure(
        self,
        orchestrator,
        sample_request,
    ):
        """Test request processing when design generation fails."""
        with patch.object(
            orchestrator.llm_parser,
            'parse_message',
            new_callable=AsyncMock,
            return_value=sample_request,
        ):
            with patch.object(
                orchestrator.design_generator,
                'generate_design',
                new_callable=AsyncMock,
                side_effect=Exception("Design generation failed"),
            ):
                result = await orchestrator.process_tshirt_request(
                    message="test message",
                    user_id="test_user",
                    username="TestUser",
                )

        assert result.success is False
        assert "Design generation failed" in result.error_message
        assert result.product_url is None

    @pytest.mark.asyncio
    async def test_process_tshirt_request_printify_failure(
        self,
        orchestrator,
        sample_request,
    ):
        """Test request processing when Printify API fails."""
        with patch.object(
            orchestrator.llm_parser,
            'parse_message',
            new_callable=AsyncMock,
            return_value=sample_request,
        ):
            with patch.object(
                orchestrator.design_generator,
                'generate_design',
                new_callable=AsyncMock,
                return_value=(Path("/tmp/test.png"), b"fake_data"),
            ):
                with patch.object(
                    orchestrator.printify_client,
                    'create_product',
                    new_callable=AsyncMock,
                    side_effect=Exception("Printify API error"),
                ):
                    result = await orchestrator.process_tshirt_request(
                        message="test message",
                        user_id="test_user",
                        username="TestUser",
                    )

        assert result.success is False
        assert "Printify API error" in result.error_message
        assert result.product_url is None

    def test_response_phrases_not_empty(self, orchestrator):
        """Test that response phrases list is not empty."""
        assert len(TShirtOrchestrator.RESPONSE_PHRASES) > 0
        assert all(isinstance(phrase, str) for phrase in TShirtOrchestrator.RESPONSE_PHRASES)
