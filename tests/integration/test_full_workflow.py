"""Integration tests for the full t-shirt creation workflow."""

import pytest
from unittest.mock import AsyncMock, patch
from pathlib import Path

from src.services.orchestrator import TShirtOrchestrator
from src.services.prodigi_client import ProdigiProduct


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
        # Mock Prodigi client
        mock_product = ProdigiProduct(
            order_id="ord_99999",
            product_id="itm_123",
            sku="GLOBAL-TSHU-CLAS-MENS-MEDI-WHIT",
            external_id="test_integration",
            name="Integration Test Product",
            thumbnail_url=None,
            retail_price=15.0,
            currency="USD",
            product_url="https://dashboard.prodigi.com/orders/ord_99999",
            status="InProgress",
        )

        with patch.object(
            orchestrator.prodigi_client,
            'initialize',
            new_callable=AsyncMock,
        ):
            with patch.object(
                orchestrator.prodigi_client,
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
                assert "ord_99999" in result.product_url
                assert result.response_phrase is not None
                assert result.error_message is None

                # Cleanup
                await orchestrator.cleanup()

    @pytest.mark.asyncio
    async def test_workflow_with_simple_phrase(self, orchestrator):
        """Test workflow with a simple phrase."""
        mock_product = ProdigiProduct(
            order_id="ord_88888",
            product_id="itm_888",
            sku="GLOBAL-TSHU-CLAS-MENS-MEDI-WHIT",
            external_id="test_simple",
            name="Simple Test",
            thumbnail_url=None,
            retail_price=15.0,
            currency="USD",
            product_url="https://dashboard.prodigi.com/orders/ord_88888",
            status="InProgress",
        )

        with patch.object(
            orchestrator.prodigi_client,
            'initialize',
            new_callable=AsyncMock,
        ):
            with patch.object(
                orchestrator.prodigi_client,
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
        mock_product = ProdigiProduct(
            order_id="ord_77777",
            product_id="itm_777",
            sku="GLOBAL-TSHU-CLAS-MENS-MEDI-WHIT",
            external_id="test_complex",
            name="Complex Test",
            thumbnail_url=None,
            retail_price=15.0,
            currency="USD",
            product_url="https://dashboard.prodigi.com/orders/ord_77777",
            status="InProgress",
        )

        with patch.object(
            orchestrator.prodigi_client,
            'initialize',
            new_callable=AsyncMock,
        ):
            with patch.object(
                orchestrator.prodigi_client,
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
        # Simulate Prodigi API failure
        with patch.object(
            orchestrator.prodigi_client,
            'initialize',
            new_callable=AsyncMock,
        ):
            with patch.object(
                orchestrator.prodigi_client,
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
