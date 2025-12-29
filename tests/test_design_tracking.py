"""Tests for design tracking features."""

import pytest
from unittest.mock import AsyncMock, MagicMock, patch

from src.services.printify_client import PrintifyClient
from src.services.orchestrator import TShirtOrchestrator


class TestDesignTracking:
    """Test suite for design tracking functionality."""

    @pytest.fixture
    def client(self):
        """Create a Printify client instance."""
        return PrintifyClient()

    @pytest.fixture
    def orchestrator(self):
        """Create an orchestrator instance."""
        return TShirtOrchestrator()

    def create_response_mock(self, json_data, status=200):
        """Helper to create properly mocked async response."""
        response = MagicMock()
        response.status = status
        response.raise_for_status = MagicMock()
        response.json = AsyncMock(return_value=json_data)
        response.text = AsyncMock(return_value=str(json_data))
        
        cm = AsyncMock()
        cm.__aenter__.return_value = response
        cm.__aexit__.return_value = None
        return cm

    @pytest.mark.asyncio
    async def test_list_products_with_pagination(self, client):
        """Test listing products with pagination."""
        await client.initialize()

        mock_cm = self.create_response_mock([
            {"id": "prod_1", "title": "Product 1", "external": {"id": "discord_123_456"}},
            {"id": "prod_2", "title": "Product 2", "external": {"id": "discord_789_012"}},
        ])

        with patch.object(client.session, 'get', return_value=mock_cm):
            result = await client.list_products(limit=10, page=1)

            assert "products" in result
            assert "paging" in result
            assert len(result["products"]) == 2

        await client.cleanup()

    @pytest.mark.asyncio
    async def test_search_products_by_user(self, client):
        """Test searching products by user ID."""
        await client.initialize()

        mock_cm = self.create_response_mock([
            {"id": "prod_1", "external": {"id": "discord_123_456"}, "title": "Product 1"},
            {"id": "prod_2", "external": {"id": "discord_789_012"}, "title": "Product 2"},
            {"id": "prod_3", "external": {"id": "discord_123_789"}, "title": "Product 3"},
        ])

        # Return empty list on second call to simulate end of pagination
        mock_cm_empty = self.create_response_mock([])

        with patch.object(client.session, 'get', side_effect=[mock_cm, mock_cm_empty]):
            designs = await client.search_products_by_user("123")

            assert len(designs) == 2  # Only products with user_id 123
            assert all("123" in d["external"]["id"] for d in designs)

        await client.cleanup()

    @pytest.mark.asyncio
    async def test_get_all_designs(self, client):
        """Test retrieving all designs."""
        await client.initialize()

        # First page with 3 products
        mock_cm_1 = self.create_response_mock([
            {"id": "prod_1", "title": "Product 1"},
            {"id": "prod_2", "title": "Product 2"},
            {"id": "prod_3", "title": "Product 3"},
        ])

        # Second page empty (end of pagination)
        mock_cm_2 = self.create_response_mock([])

        with patch.object(client.session, 'get', side_effect=[mock_cm_1, mock_cm_2]):
            designs = await client.get_all_designs()

            assert len(designs) == 3
            assert designs[0]["id"] == "prod_1"
            assert designs[2]["id"] == "prod_3"

        await client.cleanup()

    @pytest.mark.asyncio
    async def test_get_design_stats(self, client):
        """Test retrieving design statistics."""
        await client.initialize()

        mock_cm = self.create_response_mock([
            {"id": "prod_1", "external": {"id": "discord_123_456"}},
            {"id": "prod_2", "external": {"id": "discord_789_012"}},
            {"id": "prod_3", "external": {"id": "discord_123_789"}},
        ])
        
        # Empty second page to stop pagination
        mock_cm_empty = self.create_response_mock([])

        with patch.object(client.session, 'get', side_effect=[mock_cm, mock_cm_empty]):
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
            {"id": "prod_1", "title": "Design 1"},
            {"id": "prod_2", "title": "Design 2"},
        ]

        with patch.object(
            orchestrator.printify_client,
            'search_products_by_user',
            new_callable=AsyncMock,
            return_value=mock_designs,
        ):
            designs = await orchestrator.get_user_designs("123")

            assert len(designs) == 2
            assert designs[0]["title"] == "Design 1"

    @pytest.mark.asyncio
    async def test_orchestrator_get_design_statistics(self, orchestrator):
        """Test getting design statistics through orchestrator."""
        mock_stats = {
            "total_designs": 10,
            "unique_users": 5,
            "designs_per_user": 2.0,
            "latest_design": {"id": "prod_1"},
        }

        with patch.object(
            orchestrator.printify_client,
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
            {"id": "prod_1", "title": "Design 1"},
            {"id": "prod_2", "title": "Design 2"},
            {"id": "prod_3", "title": "Design 3"},
        ]

        with patch.object(
            orchestrator.printify_client,
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

        mock_cm = self.create_response_mock([])

        with patch.object(client.session, 'get', return_value=mock_cm):
            designs = await client.search_products_by_user("999")

            assert len(designs) == 0

        await client.cleanup()

    @pytest.mark.asyncio
    async def test_get_design_stats_no_designs(self, client):
        """Test design statistics when no designs exist."""
        await client.initialize()

        mock_cm = self.create_response_mock([])

        with patch.object(client.session, 'get', return_value=mock_cm):
            stats = await client.get_design_stats()

            assert stats["total_designs"] == 0
            assert stats["unique_users"] == 0
            assert stats["designs_per_user"] == 0
            assert stats["latest_design"] is None

        await client.cleanup()
