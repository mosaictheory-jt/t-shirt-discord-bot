"""
Real integration tests for Printify API.

These tests require real Printify API credentials to run.
Set the following environment variables:
- PRINTIFY_API_KEY: Your Printify API key
- PRINTIFY_SHOP_ID: Your Printify shop ID

Run with: pytest tests/integration/test_printify_integration.py -v --run-integration
"""

import logging
import os
import pytest
import aiohttp
from typing import Optional

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Skip all tests if credentials not available
PRINTIFY_API_KEY = os.environ.get("PRINTIFY_API_KEY", "")
PRINTIFY_SHOP_ID = os.environ.get("PRINTIFY_SHOP_ID", "")

# Check if we have real credentials (not test values)
HAS_REAL_CREDENTIALS = (
    PRINTIFY_API_KEY 
    and PRINTIFY_SHOP_ID 
    and PRINTIFY_API_KEY != "test_printify_key"
    and PRINTIFY_SHOP_ID != "test_shop_id"
)

pytestmark = [
    pytest.mark.integration,
    pytest.mark.skipif(
        not HAS_REAL_CREDENTIALS,
        reason="Real Printify credentials required. Set PRINTIFY_API_KEY and PRINTIFY_SHOP_ID"
    )
]


class PrintifyAPITester:
    """Helper class for testing Printify API directly."""
    
    BASE_URL = "https://api.printify.com/v1"
    
    def __init__(self, api_key: str, shop_id: str):
        self.api_key = api_key
        self.shop_id = shop_id
        self.session: Optional[aiohttp.ClientSession] = None
    
    async def __aenter__(self):
        self.session = aiohttp.ClientSession(
            headers={
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json",
            }
        )
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.session:
            await self.session.close()
    
    async def get_shops(self) -> dict:
        """Get all shops for the account."""
        async with self.session.get(f"{self.BASE_URL}/shops.json") as response:
            response.raise_for_status()
            return await response.json()
    
    async def get_shop_info(self) -> dict:
        """Get specific shop information."""
        async with self.session.get(f"{self.BASE_URL}/shops/{self.shop_id}.json") as response:
            response.raise_for_status()
            return await response.json()
    
    async def list_blueprints(self, limit: int = 10) -> list:
        """List available blueprints (product types)."""
        async with self.session.get(f"{self.BASE_URL}/catalog/blueprints.json") as response:
            response.raise_for_status()
            data = await response.json()
            return data[:limit] if isinstance(data, list) else data.get("data", [])[:limit]
    
    async def get_blueprint_details(self, blueprint_id: int) -> dict:
        """Get details for a specific blueprint."""
        async with self.session.get(
            f"{self.BASE_URL}/catalog/blueprints/{blueprint_id}.json"
        ) as response:
            response.raise_for_status()
            return await response.json()
    
    async def get_print_providers(self, blueprint_id: int) -> list:
        """Get print providers for a blueprint."""
        async with self.session.get(
            f"{self.BASE_URL}/catalog/blueprints/{blueprint_id}/print_providers.json"
        ) as response:
            response.raise_for_status()
            return await response.json()
    
    async def get_variants(self, blueprint_id: int, print_provider_id: int) -> dict:
        """Get variants for a blueprint and print provider."""
        url = f"{self.BASE_URL}/catalog/blueprints/{blueprint_id}/print_providers/{print_provider_id}/variants.json"
        async with self.session.get(url) as response:
            response.raise_for_status()
            return await response.json()
    
    async def list_products(self, limit: int = 10) -> dict:
        """List products in the shop."""
        params = {"limit": limit}
        async with self.session.get(
            f"{self.BASE_URL}/shops/{self.shop_id}/products.json",
            params=params
        ) as response:
            response.raise_for_status()
            return await response.json()
    
    async def upload_image_from_url(self, image_url: str, filename: str) -> dict:
        """Upload an image from URL."""
        payload = {
            "file_name": filename,
            "url": image_url
        }
        async with self.session.post(
            f"{self.BASE_URL}/uploads/images.json",
            json=payload
        ) as response:
            response.raise_for_status()
            return await response.json()
    
    async def create_product(
        self,
        title: str,
        blueprint_id: int,
        print_provider_id: int,
        variants: list,
        print_areas: list,
        description: str = ""
    ) -> dict:
        """Create a product in the shop."""
        payload = {
            "title": title,
            "description": description,
            "blueprint_id": blueprint_id,
            "print_provider_id": print_provider_id,
            "variants": variants,
            "print_areas": print_areas
        }
        async with self.session.post(
            f"{self.BASE_URL}/shops/{self.shop_id}/products.json",
            json=payload
        ) as response:
            response.raise_for_status()
            return await response.json()
    
    async def delete_product(self, product_id: str) -> bool:
        """Delete a product from the shop."""
        async with self.session.delete(
            f"{self.BASE_URL}/shops/{self.shop_id}/products/{product_id}.json"
        ) as response:
            return response.status == 200


@pytest.fixture
async def api_tester():
    """Create API tester with real credentials."""
    async with PrintifyAPITester(PRINTIFY_API_KEY, PRINTIFY_SHOP_ID) as tester:
        yield tester


class TestPrintifyAPIConnectivity:
    """Test basic API connectivity."""
    
    @pytest.mark.asyncio
    async def test_get_shops(self, api_tester):
        """Test that we can retrieve shops."""
        shops = await api_tester.get_shops()
        
        logger.info(f"Retrieved {len(shops)} shops")
        assert isinstance(shops, list), "Expected list of shops"
        assert len(shops) > 0, "Expected at least one shop"
        
        # Log shop details
        for shop in shops:
            logger.info(f"  Shop: {shop.get('title')} (ID: {shop.get('id')})")
    
    @pytest.mark.asyncio
    async def test_get_shop_info(self, api_tester):
        """Test that we can get shop details."""
        shop = await api_tester.get_shop_info()
        
        logger.info(f"Shop Info: {shop}")
        assert "id" in shop, "Shop should have an ID"
        assert "title" in shop, "Shop should have a title"


class TestPrintifyCatalog:
    """Test catalog operations."""
    
    @pytest.mark.asyncio
    async def test_list_blueprints(self, api_tester):
        """Test listing available blueprints."""
        blueprints = await api_tester.list_blueprints(limit=5)
        
        logger.info(f"Retrieved {len(blueprints)} blueprints")
        assert len(blueprints) > 0, "Expected at least one blueprint"
        
        for bp in blueprints:
            logger.info(f"  Blueprint: {bp.get('title')} (ID: {bp.get('id')})")
    
    @pytest.mark.asyncio
    async def test_get_tshirt_blueprint(self, api_tester):
        """Test getting t-shirt blueprint details."""
        # Blueprint ID 5 is typically "Unisex Heavy Cotton Tee"
        blueprint = await api_tester.get_blueprint_details(5)
        
        logger.info(f"T-Shirt Blueprint: {blueprint.get('title')}")
        assert blueprint.get("id") == 5
        assert "title" in blueprint
    
    @pytest.mark.asyncio
    async def test_get_print_providers(self, api_tester):
        """Test getting print providers for a blueprint."""
        providers = await api_tester.get_print_providers(5)
        
        logger.info(f"Found {len(providers)} print providers")
        assert len(providers) > 0, "Expected at least one print provider"
        
        for provider in providers[:3]:  # Log first 3
            logger.info(f"  Provider: {provider.get('title')} (ID: {provider.get('id')})")
    
    @pytest.mark.asyncio
    async def test_get_variants(self, api_tester):
        """Test getting variants for blueprint and provider."""
        # Get first available provider
        providers = await api_tester.get_print_providers(5)
        assert len(providers) > 0, "Need at least one provider"
        
        provider_id = providers[0]["id"]
        variants_data = await api_tester.get_variants(5, provider_id)
        
        variants = variants_data.get("variants", [])
        logger.info(f"Found {len(variants)} variants for provider {provider_id}")
        assert len(variants) > 0, "Expected at least one variant"
        
        # Log first few variants
        for variant in variants[:3]:
            logger.info(f"  Variant: {variant.get('title')} (ID: {variant.get('id')})")


class TestPrintifyProducts:
    """Test product operations."""
    
    @pytest.mark.asyncio
    async def test_list_products(self, api_tester):
        """Test listing products in the shop."""
        result = await api_tester.list_products(limit=5)
        
        products = result.get("data", result) if isinstance(result, dict) else result
        if isinstance(products, list):
            logger.info(f"Found {len(products)} products in shop")
            for product in products[:3]:
                logger.info(f"  Product: {product.get('title')} (ID: {product.get('id')})")
        else:
            logger.info(f"Products response: {result}")


class TestPrintifyImageUpload:
    """Test image upload functionality."""
    
    @pytest.mark.asyncio
    async def test_upload_image_from_url(self, api_tester):
        """Test uploading an image from URL."""
        # Use a publicly available test image
        test_image_url = "https://via.placeholder.com/500x500/FF0000/FFFFFF?text=Test"
        
        try:
            result = await api_tester.upload_image_from_url(
                image_url=test_image_url,
                filename="integration_test_image.png"
            )
            
            logger.info(f"Image upload result: {result}")
            assert "id" in result, "Upload should return an image ID"
            logger.info(f"Uploaded image ID: {result['id']}")
        except aiohttp.ClientResponseError as e:
            if e.status == 400:
                logger.warning(f"Image upload failed (expected for placeholder): {e}")
                pytest.skip("Placeholder image not accepted by Printify")
            raise


class TestPrintifyProductCreation:
    """Test full product creation workflow."""
    
    @pytest.mark.asyncio
    async def test_create_and_delete_product(self, api_tester):
        """Test creating and deleting a product."""
        # First, get a print provider and variants
        providers = await api_tester.get_print_providers(5)
        assert len(providers) > 0, "Need at least one provider"
        
        provider_id = providers[0]["id"]
        variants_data = await api_tester.get_variants(5, provider_id)
        variants = variants_data.get("variants", [])
        
        assert len(variants) > 0, "Need at least one variant"
        
        # Use first 3 variants
        selected_variants = [
            {
                "id": v["id"],
                "price": 2500,  # $25.00
                "is_enabled": True
            }
            for v in variants[:3]
        ]
        
        # Create product (without actual image - just testing the API)
        product = await api_tester.create_product(
            title="Integration Test Product - DELETE ME",
            blueprint_id=5,
            print_provider_id=provider_id,
            variants=selected_variants,
            print_areas=[],  # Empty for now - no image
            description="This is a test product created by integration tests"
        )
        
        logger.info(f"Created product: {product.get('id')}")
        assert "id" in product, "Product should have an ID"
        
        product_id = product["id"]
        
        # Clean up - delete the test product
        deleted = await api_tester.delete_product(product_id)
        logger.info(f"Deleted product {product_id}: {deleted}")


class TestPrintifyClientIntegration:
    """Test the PrintifyClient class with real API."""
    
    @pytest.mark.asyncio
    async def test_printify_client_initialize(self):
        """Test PrintifyClient initialization."""
        from src.services.printify_client import PrintifyClient
        
        client = PrintifyClient()
        await client.initialize()
        
        assert client.session is not None
        logger.info("PrintifyClient initialized successfully")
        
        await client.cleanup()
    
    @pytest.mark.asyncio
    async def test_printify_client_list_products(self):
        """Test PrintifyClient list_products."""
        from src.services.printify_client import PrintifyClient
        
        client = PrintifyClient()
        await client.initialize()
        
        try:
            result = await client.list_products(limit=5)
            
            logger.info(f"List products result: {result}")
            assert "products" in result
            logger.info(f"Found {len(result['products'])} products")
        finally:
            await client.cleanup()
    
    @pytest.mark.asyncio
    async def test_printify_client_get_all_designs(self):
        """Test PrintifyClient get_all_designs."""
        from src.services.printify_client import PrintifyClient
        
        client = PrintifyClient()
        await client.initialize()
        
        try:
            designs = await client.get_all_designs()
            logger.info(f"Total designs in store: {len(designs)}")
        finally:
            await client.cleanup()
    
    @pytest.mark.asyncio
    async def test_printify_client_get_design_stats(self):
        """Test PrintifyClient get_design_stats."""
        from src.services.printify_client import PrintifyClient
        
        client = PrintifyClient()
        await client.initialize()
        
        try:
            stats = await client.get_design_stats()
            
            logger.info(f"Design stats: {stats}")
            assert "total_designs" in stats
            assert "unique_users" in stats
        finally:
            await client.cleanup()


# Standalone test runner for manual testing
async def run_manual_tests():
    """Run tests manually without pytest."""
    if not HAS_REAL_CREDENTIALS:
        print("ERROR: Real Printify credentials required!")
        print("Set PRINTIFY_API_KEY and PRINTIFY_SHOP_ID environment variables")
        return
    
    print(f"Using Shop ID: {PRINTIFY_SHOP_ID}")
    print(f"API Key: {PRINTIFY_API_KEY[:10]}...{PRINTIFY_API_KEY[-4:]}")
    print()
    
    async with PrintifyAPITester(PRINTIFY_API_KEY, PRINTIFY_SHOP_ID) as tester:
        # Test 1: Get shops
        print("1. Testing get_shops...")
        try:
            shops = await tester.get_shops()
            print(f"   ✓ Found {len(shops)} shops")
            for shop in shops:
                print(f"     - {shop.get('title')} (ID: {shop.get('id')})")
        except Exception as e:
            print(f"   ✗ Error: {e}")
        
        # Test 2: List blueprints
        print("\n2. Testing list_blueprints...")
        try:
            blueprints = await tester.list_blueprints(limit=5)
            print(f"   ✓ Found {len(blueprints)} blueprints")
        except Exception as e:
            print(f"   ✗ Error: {e}")
        
        # Test 3: List products
        print("\n3. Testing list_products...")
        try:
            result = await tester.list_products(limit=5)
            products = result.get("data", result) if isinstance(result, dict) else result
            count = len(products) if isinstance(products, list) else 0
            print(f"   ✓ Found {count} products in shop")
        except Exception as e:
            print(f"   ✗ Error: {e}")
        
        print("\n✓ All basic tests completed!")


if __name__ == "__main__":
    import asyncio
    asyncio.run(run_manual_tests())
