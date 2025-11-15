"""Tests for design tracking features."""

import pytest
from unittest.mock import AsyncMock, MagicMock, patch

from src.services.printful_client import PrintfulClient
from src.services.orchestrator import TShirtOrchestrator


class TestDesignTracking:
    """Test suite for design tracking functionality."""

    @pytest.fixture
    def client(self):
        """Create a Printful client instance."""
        return PrintfulClient()

    @pytest.fixture
    def orchestrator(self):
        """Create an orchestrator instance."""
        return TShirtOrchestrator()

    @pytest.mark.asyncio
    async def test_list_products_with_pagination(self, client):
        """Test listing products with pagination."""
        await client.initialize()

        mock_response = AsyncMock()
        mock_response.raise_for_status = MagicMock()
        mock_response.json = AsyncMock(return_value={
            "result": [
                {"id": 1, "name": "Product 1"},
                {"id": 2, "name": "Product 2"},
            ],
            "paging": {"next": None}
        })

        with patch.object(client.session, 'get', return_value=mock_response):
            result = await client.list_products(limit=10, offset=0)

            assert "products" in result
            assert "paging" in result
            assert len(result["products"]) == 2

        await client.cleanup()

    @pytest.mark.asyncio
    async def test_search_products_by_user(self, client):
        """Test searching products by user ID."""
        await client.initialize()

        mock_response = AsyncMock()
        mock_response.raise_for_status = MagicMock()
        mock_response.json = AsyncMock(return_value={
            "result": [
                {"id": 1, "name": "Product 1", "external_id": "discord_123_456"},
                {"id": 2, "name": "Product 2", "external_id": "discord_789_012"},
                {"id": 3, "name": "Product 3", "external_id": "discord_123_789"},
            ],
            "paging": {"next": None}
        })

        with patch.object(client.session, 'get', return_value=mock_response):
            designs = await client.search_products_by_user("123")

            assert len(designs) == 2  # Only products with user_id 123
            assert all("123" in d["external_id"] for d in designs)

        await client.cleanup()

    @pytest.mark.asyncio
    async def test_get_all_designs(self, client):
        """Test retrieving all designs."""
        await client.initialize()

        # Mock two pages of results
        mock_response_1 = AsyncMock()
        mock_response_1.raise_for_status = MagicMock()
        mock_response_1.json = AsyncMock(return_value={
            "result": [
                {"id": 1, "name": "Product 1"},
                {"id": 2, "name": "Product 2"},
            ],
            "paging": {"next": "next_url"}
        })

        mock_response_2 = AsyncMock()
        mock_response_2.raise_for_status = MagicMock()
        mock_response_2.json = AsyncMock(return_value={
            "result": [
                {"id": 3, "name": "Product 3"},
            ],
            "paging": {"next": None}
        })

        with patch.object(
            client.session,
            'get',
            side_effect=[mock_response_1, mock_response_2]
        ):
            designs = await client.get_all_designs()

            assert len(designs) == 3
            assert designs[0]["id"] == 1
            assert designs[2]["id"] == 3

        await client.cleanup()

    @pytest.mark.asyncio
    async def test_get_design_stats(self, client):
        """Test retrieving design statistics."""
        await client.initialize()

        mock_response = AsyncMock()
        mock_response.raise_for_status = MagicMock()
        mock_response.json = AsyncMock(return_value={
            "result": [
                {"id": 1, "name": "Product 1", "external_id": "discord_123_456"},
                {"id": 2, "name": "Product 2", "external_id": "discord_789_012"},
                {"id": 3, "name": "Product 3", "external_id": "discord_123_789"},
            ],
            "paging": {"next": None}
        })

        with patch.object(client.session, 'get', return_value=mock_response):
            stats = await client.get_design_stats()

            assert stats["total_designs"] == 3
            assert stats["unique_users"] == 2  # Users 123 and 789
            assert stats["designs_per_user"] == 1.5
            assert stats["latest_design"] is not None

        await client.cleanup()

    @pytest.mark.asyncio
    async def test_orchestrator_get_user_designs(self, orchestrator):
        """Test getting user designs through orchestrator."""
        mock_designs = [
            {"id": 1, "name": "Design 1"},
            {"id": 2, "name": "Design 2"},
        ]

        with patch.object(
            orchestrator.printful_client,
            'search_products_by_user',
            new_callable=AsyncMock,
            return_value=mock_designs,
        ):
            designs = await orchestrator.get_user_designs("123")

            assert len(designs) == 2
            assert designs[0]["name"] == "Design 1"

    @pytest.mark.asyncio
    async def test_orchestrator_get_design_statistics(self, orchestrator):
        """Test getting design statistics through orchestrator."""
        mock_stats = {
            "total_designs": 10,
            "unique_users": 5,
            "designs_per_user": 2.0,
            "latest_design": {"id": 1},
        }

        with patch.object(
            orchestrator.printful_client,
            'get_design_stats',
            new_callable=AsyncMock,
            return_value=mock_stats,
        ):
            stats = await orchestrator.get_design_statistics()

            assert stats["total_designs"] == 10
            assert stats["unique_users"] == 5
            assert stats["designs_per_user"] == 2.0

    @pytest.mark.asyncio
    async def test_orchestrator_get_all_designs(self, orchestrator):
        """Test getting all designs through orchestrator."""
        mock_designs = [
            {"id": 1, "name": "Design 1"},
            {"id": 2, "name": "Design 2"},
            {"id": 3, "name": "Design 3"},
        ]

        with patch.object(
            orchestrator.printful_client,
            'get_all_designs',
            new_callable=AsyncMock,
            return_value=mock_designs,
        ):
            designs = await orchestrator.get_all_designs()

            assert len(designs) == 3

    @pytest.mark.asyncio
    async def test_search_products_by_user_empty_result(self, client):
        """Test searching products when user has no designs."""
        await client.initialize()

        mock_response = AsyncMock()
        mock_response.raise_for_status = MagicMock()
        mock_response.json = AsyncMock(return_value={
            "result": [],
            "paging": {"next": None}
        })

        with patch.object(client.session, 'get', return_value=mock_response):
            designs = await client.search_products_by_user("999")

            assert len(designs) == 0

        await client.cleanup()

    @pytest.mark.asyncio
    async def test_get_design_stats_no_designs(self, client):
        """Test design statistics when no designs exist."""
        await client.initialize()

        mock_response = AsyncMock()
        mock_response.raise_for_status = MagicMock()
        mock_response.json = AsyncMock(return_value={
            "result": [],
            "paging": {"next": None}
        })

        with patch.object(client.session, 'get', return_value=mock_response):
            stats = await client.get_design_stats()

            assert stats["total_designs"] == 0
            assert stats["unique_users"] == 0
            assert stats["designs_per_user"] == 0
            assert stats["latest_design"] is None

        await client.cleanup()
