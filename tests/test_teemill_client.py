"""Tests for Teemill API client."""

import pytest
from unittest.mock import AsyncMock, MagicMock, patch
import aiohttp

from src.services.teemill_client import TeemillClient, TeemillProduct


class TestTeemillClient:
    """Test suite for TeemillClient."""

    @pytest.fixture
    def client(self):
        """Create a client instance."""
        return TeemillClient()

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
    async def test_upload_design_image(self, client):
        """Test design image upload."""
        await client.initialize()
        
        mock_response = AsyncMock()
        mock_response.raise_for_status = MagicMock()
        mock_response.json = AsyncMock(return_value={
            "url": "https://teemill.com/designs/12345.png"
        })
        mock_response.__aenter__.return_value = mock_response
        mock_response.__aexit__.return_value = AsyncMock()
        
        with patch.object(client.session, 'post', return_value=mock_response):
            image_url = await client._upload_design_image("data:image/png;base64,abc123")
            
            assert image_url == "https://teemill.com/designs/12345.png"
        
        await client.cleanup()

    @pytest.mark.asyncio
    async def test_create_order(self, client):
        """Test order creation."""
        await client.initialize()
        
        mock_response = AsyncMock()
        mock_response.raise_for_status = MagicMock()
        mock_response.json = AsyncMock(return_value={
            "order_id": "order_123",
            "id": "order_123",
            "products": [{
                "id": "prod_456",
                "product_id": "prod_456",
                "variant_id": "var_789",
                "price": 25.0,
                "currency": "GBP",
                "thumbnail_url": "https://teemill.com/thumb.jpg"
            }],
            "url": "https://teemill.com/order/order_123"
        })
        mock_response.__aenter__.return_value = mock_response
        mock_response.__aexit__.return_value = AsyncMock()
        
        with patch.object(client.session, 'post', return_value=mock_response):
            product = await client._create_order(
                product_name="Test Product",
                image_url="https://teemill.com/designs/12345.png",
                external_id="test_123",
            )
            
            assert isinstance(product, TeemillProduct)
            assert product.order_id == "order_123"
            assert product.name == "Test Product"
            assert product.retail_price == 25.0
            assert product.product_url == "https://teemill.com/order/order_123"
        
        await client.cleanup()

    @pytest.mark.asyncio
    async def test_create_product_success(self, client):
        """Test complete product creation workflow."""
        await client.initialize()
        
        # Mock upload response
        upload_response = AsyncMock()
        upload_response.raise_for_status = MagicMock()
        upload_response.json = AsyncMock(return_value={
            "url": "https://teemill.com/designs/12345.png"
        })
        upload_response.__aenter__.return_value = upload_response
        upload_response.__aexit__.return_value = AsyncMock()
        
        # Mock order creation response
        order_response = AsyncMock()
        order_response.raise_for_status = MagicMock()
        order_response.json = AsyncMock(return_value={
            "order_id": "order_123",
            "products": [{
                "id": "prod_456",
                "price": 25.0,
                "currency": "GBP",
                "thumbnail_url": "https://teemill.com/thumb.jpg"
            }],
            "url": "https://teemill.com/order/order_123"
        })
        order_response.__aenter__.return_value = order_response
        order_response.__aexit__.return_value = AsyncMock()
        
        with patch.object(client.session, 'post', side_effect=[upload_response, order_response]):
            product = await client.create_product(
                design_image_url="data:image/png;base64,abc123",
                product_name="Test T-Shirt",
                user_id="user_123",
            )
            
            assert isinstance(product, TeemillProduct)
            assert product.order_id == "order_123"
            assert product.product_id == "prod_456"
            assert product.product_url == "https://teemill.com/order/order_123"
        
        await client.cleanup()

    @pytest.mark.asyncio
    async def test_get_product_info(self, client):
        """Test retrieving product information."""
        await client.initialize()
        
        mock_response = AsyncMock()
        mock_response.raise_for_status = MagicMock()
        mock_response.json = AsyncMock(return_value={
            "order_id": "order_123",
            "products": [{
                "id": "prod_456",
                "name": "Test Product"
            }]
        })
        mock_response.__aenter__.return_value = mock_response
        mock_response.__aexit__.return_value = AsyncMock()
        
        with patch.object(client.session, 'get', return_value=mock_response):
            info = await client.get_product_info("order_123")
            
            assert info["order_id"] == "order_123"
            assert info["products"][0]["name"] == "Test Product"
        
        await client.cleanup()

    @pytest.mark.asyncio
    async def test_list_products(self, client):
        """Test listing all products."""
        await client.initialize()
        
        mock_response = AsyncMock()
        mock_response.raise_for_status = MagicMock()
        mock_response.json = AsyncMock(return_value={
            "orders": [
                {"id": "order_1", "order_id": "order_1"},
                {"id": "order_2", "order_id": "order_2"}
            ],
            "total": 2
        })
        mock_response.__aenter__.return_value = mock_response
        mock_response.__aexit__.return_value = AsyncMock()
        
        with patch.object(client.session, 'get', return_value=mock_response):
            result = await client.list_products()
            
            assert "products" in result
            assert len(result["products"]) == 2
            assert result["products"][0]["id"] == "order_1"
            assert result["products"][1]["order_id"] == "order_2"
        
        await client.cleanup()
