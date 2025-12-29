"""Integration tests for the full t-shirt creation workflow."""

import pytest
from unittest.mock import AsyncMock, patch
from pathlib import Path

from src.services.orchestrator import TShirtOrchestrator
from src.services.printify_client import PrintifyProduct


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
        # Mock Printify client
        mock_product = PrintifyProduct(
            product_id="prod_123",
            title="Integration Test Product",
            description="Test product",
            blueprint_id=5,
            print_provider_id=99,
            variant_id=101,
            external_id="test_integration",
            thumbnail_url="https://example.com/thumb.jpg",
            retail_price=29.99,
            currency="USD",
            product_url="https://printify.com/app/products/prod_123",
            publish_status="unpublished",
        )

        with patch.object(
            orchestrator.printify_client,
            'initialize',
            new_callable=AsyncMock,
        ):
            with patch.object(
                orchestrator.printify_client,
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
                assert "order_99999" in result.product_url
                assert result.response_phrase is not None
                assert result.error_message is None

                # Cleanup
                await orchestrator.cleanup()

    @pytest.mark.asyncio
    async def test_workflow_with_simple_phrase(self, orchestrator):
        """Test workflow with a simple phrase."""
        mock_product = PrintifyProduct(
            product_id="prod_888",
            title="Simple Test",
            description="Test product",
            blueprint_id=5,
            print_provider_id=99,
            variant_id=101,
            external_id="test_simple",
            thumbnail_url="https://example.com/thumb.jpg",
            retail_price=29.99,
            currency="USD",
            product_url="https://printify.com/app/products/prod_888",
            publish_status="unpublished",
        )

        with patch.object(
            orchestrator.printify_client,
            'initialize',
            new_callable=AsyncMock,
        ):
            with patch.object(
                orchestrator.printify_client,
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
        mock_product = PrintifyProduct(
            product_id="prod_777",
            title="Complex Test",
            description="Test product",
            blueprint_id=5,
            print_provider_id=99,
            variant_id=101,
            external_id="test_complex",
            thumbnail_url="https://example.com/thumb.jpg",
            retail_price=29.99,
            currency="USD",
            product_url="https://printify.com/app/products/prod_777",
            publish_status="unpublished",
        )

        with patch.object(
            orchestrator.printify_client,
            'initialize',
            new_callable=AsyncMock,
        ):
            with patch.object(
                orchestrator.printify_client,
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
        # Simulate Printify API failure
        with patch.object(
            orchestrator.printify_client,
            'initialize',
            new_callable=AsyncMock,
        ):
            with patch.object(
                orchestrator.printify_client,
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
