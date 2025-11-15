"""Tests for Printful API client."""

import pytest
from unittest.mock import AsyncMock, MagicMock, patch
import aiohttp

from src.services.printful_client import PrintfulClient, PrintfulProduct


class TestPrintfulClient:
    """Test suite for PrintfulClient."""

    @pytest.fixture
    def client(self):
        """Create a client instance."""
        return PrintfulClient()

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
    async def test_upload_design_file(self, client):
        """Test design file upload."""
        await client.initialize()
        
        mock_response = AsyncMock()
        mock_response.raise_for_status = MagicMock()
        mock_response.json = AsyncMock(return_value={
            "result": {"id": 12345}
        })
        
        with patch.object(client.session, 'post', return_value=mock_response):
            file_id = await client._upload_design_file("data:image/png;base64,abc123")
            
            assert file_id == 12345
        
        await client.cleanup()

    @pytest.mark.asyncio
    async def test_create_sync_product(self, client):
        """Test sync product creation."""
        await client.initialize()
        
        mock_response = AsyncMock()
        mock_response.raise_for_status = MagicMock()
        mock_response.json = AsyncMock(return_value={
            "result": {
                "sync_product": {
                    "id": 67890,
                    "name": "Test Product",
                    "thumbnail_url": "https://example.com/thumb.jpg"
                },
                "sync_variants": [{
                    "id": 111,
                    "retail_price": "29.99",
                    "currency": "USD"
                }]
            }
        })
        
        with patch.object(client.session, 'post', return_value=mock_response):
            product = await client._create_sync_product(
                product_id=71,
                variant_id=4012,
                file_id=12345,
                product_name="Test Product",
                external_id="test_123",
            )
            
            assert isinstance(product, PrintfulProduct)
            assert product.sync_product_id == 67890
            assert product.name == "Test Product"
            assert product.retail_price == 29.99
        
        await client.cleanup()

    @pytest.mark.asyncio
    async def test_create_product_success(self, client):
        """Test complete product creation workflow."""
        await client.initialize()
        
        # Mock upload response
        upload_response = AsyncMock()
        upload_response.raise_for_status = MagicMock()
        upload_response.json = AsyncMock(return_value={
            "result": {"id": 12345}
        })
        
        # Mock sync product response
        sync_response = AsyncMock()
        sync_response.raise_for_status = MagicMock()
        sync_response.json = AsyncMock(return_value={
            "result": {
                "sync_product": {
                    "id": 67890,
                    "name": "Test Product",
                    "thumbnail_url": "https://example.com/thumb.jpg"
                },
                "sync_variants": [{
                    "id": 111,
                    "retail_price": "29.99",
                    "currency": "USD"
                }]
            }
        })
        
        with patch.object(client.session, 'post', side_effect=[upload_response, sync_response]):
            product = await client.create_product(
                design_image_url="data:image/png;base64,abc123",
                product_name="Test T-Shirt",
                user_id="user_123",
            )
            
            assert isinstance(product, PrintfulProduct)
            assert product.sync_product_id == 67890
            assert product.product_id == 71
            assert product.variant_id == 4012
        
        await client.cleanup()

    @pytest.mark.asyncio
    async def test_get_product_info(self, client):
        """Test retrieving product information."""
        await client.initialize()
        
        mock_response = AsyncMock()
        mock_response.raise_for_status = MagicMock()
        mock_response.json = AsyncMock(return_value={
            "result": {
                "sync_product": {
                    "id": 12345,
                    "name": "Test Product"
                }
            }
        })
        
        with patch.object(client.session, 'get', return_value=mock_response):
            info = await client.get_product_info(12345)
            
            assert info["sync_product"]["id"] == 12345
            assert info["sync_product"]["name"] == "Test Product"
        
        await client.cleanup()

    @pytest.mark.asyncio
    async def test_list_products(self, client):
        """Test listing all products."""
        await client.initialize()
        
        mock_response = AsyncMock()
        mock_response.raise_for_status = MagicMock()
        mock_response.json = AsyncMock(return_value={
            "result": [
                {"id": 1, "name": "Product 1"},
                {"id": 2, "name": "Product 2"}
            ]
        })
        
        with patch.object(client.session, 'get', return_value=mock_response):
            products = await client.list_products()
            
            assert len(products) == 2
            assert products[0]["id"] == 1
            assert products[1]["name"] == "Product 2"
        
        await client.cleanup()
