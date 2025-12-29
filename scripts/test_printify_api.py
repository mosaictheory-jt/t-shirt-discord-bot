#!/usr/bin/env python3
"""
Simple script to test Printify API connectivity.

Usage:
    # With environment variables:
    PRINTIFY_API_KEY=your_key PRINTIFY_SHOP_ID=your_shop python scripts/test_printify_api.py
    
    # Or with .env file in workspace root
    python scripts/test_printify_api.py
"""

import asyncio
import logging
import os
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent))

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


async def test_api_connectivity():
    """Test basic Printify API connectivity."""
    import aiohttp
    
    api_key = os.environ.get("PRINTIFY_API_KEY", "")
    shop_id = os.environ.get("PRINTIFY_SHOP_ID", "")
    
    if not api_key or api_key == "test_printify_key":
        logger.error("PRINTIFY_API_KEY not set or using test value")
        return False
    
    if not shop_id or shop_id == "test_shop_id":
        logger.error("PRINTIFY_SHOP_ID not set or using test value")
        return False
    
    logger.info(f"Testing with Shop ID: {shop_id}")
    logger.info(f"API Key: {api_key[:10]}...{api_key[-4:] if len(api_key) > 14 else '****'}")
    
    base_url = "https://api.printify.com/v1"
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
    }
    
    async with aiohttp.ClientSession(headers=headers) as session:
        # Test 1: Get shops
        logger.info("\n=== Test 1: Get Shops ===")
        try:
            async with session.get(f"{base_url}/shops.json") as response:
                if response.status == 200:
                    shops = await response.json()
                    logger.info(f"✓ Success! Found {len(shops)} shop(s)")
                    for shop in shops:
                        logger.info(f"  - {shop.get('title')} (ID: {shop.get('id')}, Sales Channel: {shop.get('sales_channel_id')})")
                else:
                    error = await response.text()
                    logger.error(f"✗ Failed with status {response.status}: {error}")
                    return False
        except Exception as e:
            logger.error(f"✗ Error: {e}")
            return False
        
        # Test 2: Get specific shop
        logger.info("\n=== Test 2: Get Shop Info ===")
        try:
            async with session.get(f"{base_url}/shops/{shop_id}.json") as response:
                if response.status == 200:
                    shop = await response.json()
                    logger.info(f"✓ Shop: {shop.get('title')}")
                    logger.info(f"  ID: {shop.get('id')}")
                    logger.info(f"  Sales Channel: {shop.get('sales_channel_id')}")
                else:
                    error = await response.text()
                    logger.error(f"✗ Failed with status {response.status}: {error}")
        except Exception as e:
            logger.error(f"✗ Error: {e}")
        
        # Test 3: List blueprints
        logger.info("\n=== Test 3: List Blueprints (First 5) ===")
        try:
            async with session.get(f"{base_url}/catalog/blueprints.json") as response:
                if response.status == 200:
                    blueprints = await response.json()
                    logger.info(f"✓ Found {len(blueprints)} blueprints total")
                    for bp in blueprints[:5]:
                        logger.info(f"  - {bp.get('title')} (ID: {bp.get('id')})")
                else:
                    error = await response.text()
                    logger.error(f"✗ Failed with status {response.status}: {error}")
        except Exception as e:
            logger.error(f"✗ Error: {e}")
        
        # Test 4: Get T-shirt blueprint details
        logger.info("\n=== Test 4: Get T-Shirt Blueprint (ID: 5) ===")
        try:
            async with session.get(f"{base_url}/catalog/blueprints/5.json") as response:
                if response.status == 200:
                    blueprint = await response.json()
                    logger.info(f"✓ Blueprint: {blueprint.get('title')}")
                    logger.info(f"  Brand: {blueprint.get('brand')}")
                    logger.info(f"  Model: {blueprint.get('model')}")
                else:
                    error = await response.text()
                    logger.error(f"✗ Failed with status {response.status}: {error}")
        except Exception as e:
            logger.error(f"✗ Error: {e}")
        
        # Test 5: Get print providers for t-shirt
        logger.info("\n=== Test 5: Get Print Providers for T-Shirt ===")
        try:
            async with session.get(f"{base_url}/catalog/blueprints/5/print_providers.json") as response:
                if response.status == 200:
                    providers = await response.json()
                    logger.info(f"✓ Found {len(providers)} print providers")
                    for provider in providers[:3]:
                        logger.info(f"  - {provider.get('title')} (ID: {provider.get('id')})")
                else:
                    error = await response.text()
                    logger.error(f"✗ Failed with status {response.status}: {error}")
        except Exception as e:
            logger.error(f"✗ Error: {e}")
        
        # Test 6: List products in shop
        logger.info("\n=== Test 6: List Products in Shop ===")
        try:
            async with session.get(f"{base_url}/shops/{shop_id}/products.json?limit=5") as response:
                if response.status == 200:
                    result = await response.json()
                    products = result.get("data", result) if isinstance(result, dict) else result
                    if isinstance(products, list):
                        logger.info(f"✓ Found {len(products)} product(s)")
                        for product in products[:3]:
                            logger.info(f"  - {product.get('title')} (ID: {product.get('id')})")
                    else:
                        logger.info(f"✓ Response: {result}")
                else:
                    error = await response.text()
                    logger.error(f"✗ Failed with status {response.status}: {error}")
        except Exception as e:
            logger.error(f"✗ Error: {e}")
        
        logger.info("\n=== All Tests Completed ===")
        return True


async def test_printify_client():
    """Test the PrintifyClient class."""
    logger.info("\n=== Testing PrintifyClient Class ===")
    
    try:
        from src.services.printify_client import PrintifyClient
        
        client = PrintifyClient()
        await client.initialize()
        logger.info("✓ PrintifyClient initialized")
        
        # Test list_products
        result = await client.list_products(limit=5)
        logger.info(f"✓ list_products returned {len(result.get('products', []))} products")
        
        # Test get_all_designs
        designs = await client.get_all_designs()
        logger.info(f"✓ get_all_designs returned {len(designs)} designs")
        
        # Test get_design_stats
        stats = await client.get_design_stats()
        logger.info(f"✓ get_design_stats: {stats}")
        
        await client.cleanup()
        logger.info("✓ PrintifyClient cleaned up")
        
        return True
    except Exception as e:
        logger.error(f"✗ PrintifyClient test failed: {e}")
        return False


async def main():
    """Run all tests."""
    logger.info("=" * 60)
    logger.info("Printify API Integration Test")
    logger.info("=" * 60)
    
    # Check for .env file
    env_file = Path(__file__).parent.parent / ".env"
    if env_file.exists():
        logger.info(f"Loading .env from {env_file}")
        try:
            from dotenv import load_dotenv
            load_dotenv(env_file)
        except ImportError:
            logger.warning("python-dotenv not installed, reading .env manually")
            with open(env_file) as f:
                for line in f:
                    line = line.strip()
                    if line and not line.startswith("#") and "=" in line:
                        key, value = line.split("=", 1)
                        os.environ[key.strip()] = value.strip()
    
    # Run basic API tests
    api_ok = await test_api_connectivity()
    
    if api_ok:
        # Run PrintifyClient tests
        await test_printify_client()
    
    logger.info("\n" + "=" * 60)
    logger.info("Test Complete!")
    logger.info("=" * 60)


if __name__ == "__main__":
    asyncio.run(main())
