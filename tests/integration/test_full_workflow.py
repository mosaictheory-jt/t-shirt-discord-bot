"""Integration tests for the full t-shirt creation workflow."""

import pytest
from unittest.mock import AsyncMock, patch
from pathlib import Path

from src.services.orchestrator import TShirtOrchestrator
from src.services.printful_client import PrintfulProduct


@pytest.mark.integration
class TestFullWorkflow:
    """Integration tests for complete workflow."""

    @pytest.fixture
    def orchestrator(self):
        """Create an orchestrator instance."""
        return TShirtOrchestrator()

    @pytest.mark.asyncio
    async def test_complete_workflow_mock_apis(self, orchestrator):
        """Test complete workflow with mocked external APIs."""
        # Mock Printful client
        mock_product = PrintfulProduct(
            product_id=71,
            variant_id=4012,
            sync_product_id=99999,
            external_id="test_integration",
            name="Integration Test Product",
            thumbnail_url="https://example.com/thumb.jpg",
            retail_price=29.99,
            currency="USD",
        )

        with patch.object(
            orchestrator.printful_client,
            'initialize',
            new_callable=AsyncMock,
        ):
            with patch.object(
                orchestrator.printful_client,
                'create_product',
                new_callable=AsyncMock,
                return_value=mock_product,
            ):
                # Initialize
                await orchestrator.initialize()

                # Process a realistic request
                result = await orchestrator.process_tshirt_request(
                    message="Hey! I want a cool retro t-shirt that says 'Born to Code' in blue",
                    user_id="integration_test_user",
                    username="IntegrationTester#0001",
                )

                # Verify success
                assert result.success is True
                assert result.product_url is not None
                assert "99999" in result.product_url
                assert result.response_phrase is not None
                assert result.error_message is None

                # Cleanup
                await orchestrator.cleanup()

    @pytest.mark.asyncio
    async def test_workflow_with_simple_phrase(self, orchestrator):
        """Test workflow with a simple phrase."""
        mock_product = PrintfulProduct(
            product_id=71,
            variant_id=4012,
            sync_product_id=88888,
            external_id="test_simple",
            name="Simple Test",
            thumbnail_url="https://example.com/thumb.jpg",
            retail_price=29.99,
            currency="USD",
        )

        with patch.object(
            orchestrator.printful_client,
            'initialize',
            new_callable=AsyncMock,
        ):
            with patch.object(
                orchestrator.printful_client,
                'create_product',
                new_callable=AsyncMock,
                return_value=mock_product,
            ):
                await orchestrator.initialize()

                result = await orchestrator.process_tshirt_request(
                    message="shirt with Hello World",
                    user_id="test_user_2",
                    username="TestUser2",
                )

                assert result.success is True
                assert result.product_url is not None

                await orchestrator.cleanup()

    @pytest.mark.asyncio
    async def test_workflow_with_complex_request(self, orchestrator):
        """Test workflow with complex multi-part request."""
        mock_product = PrintfulProduct(
            product_id=71,
            variant_id=4012,
            sync_product_id=77777,
            external_id="test_complex",
            name="Complex Test",
            thumbnail_url="https://example.com/thumb.jpg",
            retail_price=29.99,
            currency="USD",
        )

        with patch.object(
            orchestrator.printful_client,
            'initialize',
            new_callable=AsyncMock,
        ):
            with patch.object(
                orchestrator.printful_client,
                'create_product',
                new_callable=AsyncMock,
                return_value=mock_product,
            ):
                await orchestrator.initialize()

                result = await orchestrator.process_tshirt_request(
                    message=(
                        "I really need a super cool vintage style t-shirt "
                        "that says 'Coffee First, Code Later' in a nice brown color, "
                        "maybe with some retro vibes"
                    ),
                    user_id="test_user_3",
                    username="TestUser3",
                )

                assert result.success is True
                assert result.product_url is not None
                assert result.phrase is not None

                await orchestrator.cleanup()

    @pytest.mark.asyncio
    async def test_error_recovery(self, orchestrator):
        """Test that system handles errors gracefully."""
        # Simulate Printful API failure
        with patch.object(
            orchestrator.printful_client,
            'initialize',
            new_callable=AsyncMock,
        ):
            with patch.object(
                orchestrator.printful_client,
                'create_product',
                new_callable=AsyncMock,
                side_effect=Exception("API Timeout"),
            ):
                await orchestrator.initialize()

                result = await orchestrator.process_tshirt_request(
                    message="Make me a shirt",
                    user_id="test_user_error",
                    username="ErrorUser",
                )

                # Should handle error gracefully
                assert result.success is False
                assert result.error_message is not None
                assert "API Timeout" in result.error_message

                await orchestrator.cleanup()
