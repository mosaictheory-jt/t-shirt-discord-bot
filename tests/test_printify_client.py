"""Tests for Printify API client."""

import pytest
from unittest.mock import AsyncMock, MagicMock, patch
import aiohttp

from src.services.printify_client import PrintifyClient, PrintifyProduct


class TestPrintifyClient:
    """Test suite for PrintifyClient."""

    @pytest.fixture
    def client(self):
        """Create a client instance."""
        return PrintifyClient()

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
            "id": "12345abc"
        })
        mock_response.__aenter__.return_value = mock_response
        mock_response.__aexit__.return_value = AsyncMock()
        
        with patch.object(client.session, 'post', return_value=mock_response):
            image_id = await client._upload_design_image("data:image/png;base64,abc123", "test_design")
            
            assert image_id == "12345abc"
        
        await client.cleanup()

    @pytest.mark.asyncio
    async def test_get_blueprint(self, client):
        """Test getting blueprint details."""
        await client.initialize()
        
        mock_response = AsyncMock()
        mock_response.raise_for_status = MagicMock()
        mock_response.json = AsyncMock(return_value={
            "id": 5,
            "variants": [
                {
                    "id": 101,
                    "title": "S / Black",
                    "options": {"front": "front_placeholder"}
                },
                {
                    "id": 102,
                    "title": "M / Black",
                    "options": {"front": "front_placeholder"}
                }
            ]
        })
        mock_response.__aenter__.return_value = mock_response
        mock_response.__aexit__.return_value = AsyncMock()
        
        with patch.object(client.session, 'get', return_value=mock_response):
            blueprint = await client._get_blueprint(5, 99)
            
            assert blueprint["id"] == 5
            assert len(blueprint["variants"]) == 2
        
        await client.cleanup()

    @pytest.mark.asyncio
    async def test_create_product_method(self, client):
        """Test product creation method."""
        await client.initialize()
        
        # Create a proper async context manager mock
        mock_response = MagicMock()
        mock_response.status = 200
        mock_response.raise_for_status = MagicMock()
        mock_response.json = AsyncMock(return_value={
            "id": "prod_123",
            "title": "Test Product",
            "description": "Test description",
            "blueprint_id": 5,
            "print_provider_id": 99,
            "variants": [{
                "id": 101,
                "price": 2500,
                "is_enabled": True
            }],
            "images": [{
                "src": "https://printify.com/image.png"
            }],
            "visible": False
        })
        mock_response.text = AsyncMock(return_value="")
        
        # Create async context manager
        async_cm = AsyncMock()
        async_cm.__aenter__.return_value = mock_response
        async_cm.__aexit__.return_value = None
        
        blueprint = {
            "variants": [
                {
                    "id": 101,
                    "title": "S / Black",
                    "options": {"front": "front_placeholder"},
                    "placeholders": [{"position": "front"}]
                }
            ]
        }
        
        with patch.object(client.session, 'post', return_value=async_cm):
            product = await client._create_product(
                product_name="Test Product",
                description="Test description",
                blueprint_id=5,
                print_provider_id=99,
                image_id="img_123",
                external_id="test_123",
                blueprint=blueprint,
            )
            
            assert isinstance(product, PrintifyProduct)
            assert product.product_id == "prod_123"
            assert product.title == "Test Product"
            assert product.retail_price == 25.0
            assert product.product_url == "https://printify.com/app/products/prod_123"
        
        await client.cleanup()

    @pytest.mark.asyncio
    async def test_create_product_success(self, client):
        """Test complete product creation workflow."""
        await client.initialize()
        
        # Helper to create async context manager mock
        def create_response_mock(json_data, status=200):
            response = MagicMock()
            response.status = status
            response.raise_for_status = MagicMock()
            response.json = AsyncMock(return_value=json_data)
            response.text = AsyncMock(return_value="")
            
            cm = AsyncMock()
            cm.__aenter__.return_value = response
            cm.__aexit__.return_value = None
            return cm
        
        # Mock providers response
        providers_cm = create_response_mock([
            {"id": 99, "title": "Test Provider"}
        ])
        
        # Mock upload response
        upload_cm = create_response_mock({
            "id": "img_12345"
        })
        
        # Mock blueprint response
        blueprint_cm = create_response_mock({
            "id": 5,
            "variants": [
                {
                    "id": 101,
                    "title": "S / Black",
                    "options": {"front": "front_placeholder"},
                    "placeholders": [{"position": "front"}]
                }
            ]
        })
        
        # Mock product creation response
        product_cm = create_response_mock({
            "id": "prod_456",
            "title": "Test T-Shirt - Custom Tee",
            "description": "Custom design created by user user_123",
            "blueprint_id": 5,
            "print_provider_id": 99,
            "variants": [{
                "id": 101,
                "price": 2500
            }],
            "images": [{
                "src": "https://printify.com/thumb.jpg"
            }],
            "visible": False
        })
        
        with patch.object(client.session, 'post', side_effect=[upload_cm, product_cm]):
            with patch.object(client.session, 'get', side_effect=[providers_cm, blueprint_cm]):
                product = await client.create_product(
                    design_image_url="data:image/png;base64,abc123",
                    product_name="Test T-Shirt",
                    user_id="user_123",
                )
                
                assert isinstance(product, PrintifyProduct)
                assert product.product_id == "prod_456"
                assert product.product_url == "https://printify.com/app/products/prod_456"
        
        await client.cleanup()

    @pytest.mark.asyncio
    async def test_get_product_info(self, client):
        """Test retrieving product information."""
        await client.initialize()
        
        mock_response = AsyncMock()
        mock_response.raise_for_status = MagicMock()
        mock_response.json = AsyncMock(return_value={
            "id": "prod_123",
            "title": "Test Product",
            "variants": [{
                "id": 101,
                "title": "S / Black"
            }]
        })
        mock_response.__aenter__.return_value = mock_response
        mock_response.__aexit__.return_value = AsyncMock()
        
        with patch.object(client.session, 'get', return_value=mock_response):
            info = await client.get_product_info("prod_123")
            
            assert info["id"] == "prod_123"
            assert info["title"] == "Test Product"
        
        await client.cleanup()

    @pytest.mark.asyncio
    async def test_list_products(self, client):
        """Test listing all products."""
        await client.initialize()
        
        mock_response = AsyncMock()
        mock_response.status = 200
        mock_response.raise_for_status = MagicMock()
        mock_response.json = AsyncMock(return_value=[
            {"id": "prod_1", "title": "Product 1"},
            {"id": "prod_2", "title": "Product 2"}
        ])
        mock_response.__aenter__.return_value = mock_response
        mock_response.__aexit__.return_value = AsyncMock()
        
        with patch.object(client.session, 'get', return_value=mock_response):
            result = await client.list_products()
            
            assert "products" in result
            assert len(result["products"]) == 2
            assert result["products"][0]["id"] == "prod_1"
            assert result["products"][1]["id"] == "prod_2"
        
        await client.cleanup()

    @pytest.mark.asyncio
    async def test_publish_product(self, client):
        """Test publishing a product."""
        await client.initialize()
        
        mock_response = AsyncMock()
        mock_response.raise_for_status = MagicMock()
        mock_response.json = AsyncMock(return_value={
            "success": True
        })
        mock_response.__aenter__.return_value = mock_response
        mock_response.__aexit__.return_value = AsyncMock()
        
        with patch.object(client.session, 'post', return_value=mock_response):
            result = await client.publish_product("prod_123")
            
            assert result["success"] is True
        
        await client.cleanup()
