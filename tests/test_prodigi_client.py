"""Tests for Prodigi Print API client."""

import pytest
from unittest.mock import AsyncMock, MagicMock, patch
import aiohttp

from src.services.prodigi_client import ProdigiClient, ProdigiProduct


class TestProdigiClient:
    """Test suite for ProdigiClient."""

    @pytest.fixture
    def client(self):
        """Create a client instance."""
        return ProdigiClient()

    @pytest.mark.asyncio
    async def test_initialize(self, client):
        """Test client initialization."""
        await client.initialize()
        
        assert client.session is not None
        assert isinstance(client.session, aiohttp.ClientSession)
        
        await client.cleanup()

    @pytest.mark.asyncio
    async def test_cleanup(self, client):
        """Test client cleanup."""
        await client.initialize()
        await client.cleanup()
        
        assert client.session is None

    @pytest.mark.asyncio
    async def test_upload_design_image_url(self, client):
        """Test design image handling for URLs."""
        await client.initialize()
        
        # If it's already a URL, it should return as-is
        url = "https://example.com/image.png"
        result = await client._upload_design_image(url)
        assert result == url
        
        await client.cleanup()

    @pytest.mark.asyncio
    async def test_upload_design_image_base64(self, client):
        """Test design image handling for base64."""
        await client.initialize()
        
        # For base64, it should return as-is (Prodigi accepts it in order creation)
        base64_data = "data:image/png;base64,abc123"
        result = await client._upload_design_image(base64_data)
        assert result == base64_data
        
        await client.cleanup()

    @pytest.mark.asyncio
    async def test_create_order(self, client):
        """Test order creation."""
        await client.initialize()
        
        mock_response = AsyncMock()
        mock_response.raise_for_status = MagicMock()
        mock_response.json = AsyncMock(return_value={
            "order": {
                "id": "ord_123456",
                "items": [{
                    "id": "itm_789",
                    "sku": "GLOBAL-TSHU-CLAS-MENS-MEDI-WHIT",
                    "cost": {
                        "amount": 15.0,
                        "currency": "USD"
                    }
                }],
                "status": {
                    "stage": "InProgress"
                }
            }
        })
        mock_response.__aenter__.return_value = mock_response
        mock_response.__aexit__.return_value = AsyncMock()
        
        with patch.object(client.session, 'post', return_value=mock_response):
            product = await client._create_order(
                product_name="Test Product",
                image_url="https://example.com/design.png",
                external_id="test_123",
            )
            
            assert isinstance(product, ProdigiProduct)
            assert product.order_id == "ord_123456"
            assert product.name == "Test Product"
            assert product.retail_price == 15.0
            assert product.currency == "USD"
            assert "dashboard.prodigi.com" in product.product_url
        
        await client.cleanup()

    @pytest.mark.asyncio
    async def test_create_product_success(self, client):
        """Test complete product creation workflow."""
        await client.initialize()
        
        # Mock order creation response
        order_response = AsyncMock()
        order_response.raise_for_status = MagicMock()
        order_response.json = AsyncMock(return_value={
            "order": {
                "id": "ord_123456",
                "items": [{
                    "id": "itm_789",
                    "sku": "GLOBAL-TSHU-CLAS-MENS-MEDI-WHIT",
                    "cost": {
                        "amount": 15.0,
                        "currency": "USD"
                    }
                }],
                "status": {
                    "stage": "InProgress"
                }
            }
        })
        order_response.__aenter__.return_value = order_response
        order_response.__aexit__.return_value = AsyncMock()
        
        with patch.object(client.session, 'post', return_value=order_response):
            product = await client.create_product(
                design_image_url="data:image/png;base64,abc123",
                product_name="Test T-Shirt",
                user_id="user_123",
            )
            
            assert isinstance(product, ProdigiProduct)
            assert product.order_id == "ord_123456"
            assert product.product_id == "itm_789"
            assert "dashboard.prodigi.com" in product.product_url
        
        await client.cleanup()

    @pytest.mark.asyncio
    async def test_get_product_info(self, client):
        """Test retrieving product information."""
        await client.initialize()
        
        mock_response = AsyncMock()
        mock_response.raise_for_status = MagicMock()
        mock_response.json = AsyncMock(return_value={
            "order": {
                "id": "ord_123456",
                "items": [{
                    "id": "itm_789",
                    "merchantReference": "test_ref"
                }]
            }
        })
        mock_response.__aenter__.return_value = mock_response
        mock_response.__aexit__.return_value = AsyncMock()
        
        with patch.object(client.session, 'get', return_value=mock_response):
            info = await client.get_product_info("ord_123456")
            
            assert info["order"]["id"] == "ord_123456"
            assert info["order"]["items"][0]["id"] == "itm_789"
        
        await client.cleanup()

    @pytest.mark.asyncio
    async def test_list_products(self, client):
        """Test listing all products."""
        await client.initialize()
        
        mock_response = AsyncMock()
        mock_response.raise_for_status = MagicMock()
        mock_response.status = 200
        mock_response.json = AsyncMock(return_value={
            "orders": [
                {"id": "ord_1", "merchantReference": "ref_1"},
                {"id": "ord_2", "merchantReference": "ref_2"}
            ]
        })
        mock_response.__aenter__.return_value = mock_response
        mock_response.__aexit__.return_value = AsyncMock()
        
        with patch.object(client.session, 'get', return_value=mock_response):
            result = await client.list_products()
            
            assert "products" in result
            assert len(result["products"]) == 2
            assert result["products"][0]["id"] == "ord_1"
            assert result["products"][1]["merchantReference"] == "ref_2"
        
        await client.cleanup()

    @pytest.mark.asyncio
    async def test_search_products_by_user(self, client):
        """Test searching products by user ID."""
        await client.initialize()
        
        mock_response = AsyncMock()
        mock_response.raise_for_status = MagicMock()
        mock_response.status = 200
        mock_response.json = AsyncMock(return_value={
            "orders": [
                {"id": "ord_1", "merchantReference": "discord_user123_12345"},
                {"id": "ord_2", "merchantReference": "discord_user456_67890"},
                {"id": "ord_3", "merchantReference": "discord_user123_98765"}
            ]
        })
        mock_response.__aenter__.return_value = mock_response
        mock_response.__aexit__.return_value = AsyncMock()
        
        with patch.object(client.session, 'get', return_value=mock_response):
            result = await client.search_products_by_user("user123")
            
            # Should only return orders with user123 in the reference
            assert len(result) == 2
            assert all("user123" in p["merchantReference"] for p in result)
        
        await client.cleanup()

    @pytest.mark.asyncio
    async def test_get_design_stats(self, client):
        """Test getting design statistics."""
        await client.initialize()
        
        mock_response = AsyncMock()
        mock_response.raise_for_status = MagicMock()
        mock_response.status = 200
        mock_response.json = AsyncMock(return_value={
            "orders": [
                {"id": "ord_1", "merchantReference": "discord_user123_12345"},
                {"id": "ord_2", "merchantReference": "discord_user456_67890"},
                {"id": "ord_3", "merchantReference": "discord_user123_98765"}
            ]
        })
        mock_response.__aenter__.return_value = mock_response
        mock_response.__aexit__.return_value = AsyncMock()
        
        with patch.object(client.session, 'get', return_value=mock_response):
            stats = await client.get_design_stats()
            
            assert stats["total_designs"] == 3
            assert stats["unique_users"] == 2  # user123 and user456
            assert stats["designs_per_user"] == 1.5
        
        await client.cleanup()
