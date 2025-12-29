#!/usr/bin/env python3
"""
Quick test for Printify API - pass credentials as arguments.

Usage:
    python scripts/quick_test_printify.py <API_KEY> <SHOP_ID>
"""

import asyncio
import sys
import logging

logging.basicConfig(level=logging.INFO, format="%(message)s")
logger = logging.getLogger(__name__)


async def test_printify(api_key: str, shop_id: str):
    """Test Printify API connectivity."""
    import aiohttp
    
    base_url = "https://api.printify.com/v1"
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
    }
    
    results = {"passed": 0, "failed": 0}
    
    async with aiohttp.ClientSession(headers=headers) as session:
        # Test 1: Get shops
        logger.info("1. Testing GET /shops.json...")
        try:
            async with session.get(f"{base_url}/shops.json") as response:
                if response.status == 200:
                    shops = await response.json()
                    logger.info(f"   ✓ Found {len(shops)} shop(s)")
                    for shop in shops:
                        logger.info(f"     - {shop.get('title')} (ID: {shop.get('id')})")
                    results["passed"] += 1
                else:
                    error = await response.text()
                    logger.error(f"   ✗ Status {response.status}: {error[:200]}")
                    results["failed"] += 1
        except Exception as e:
            logger.error(f"   ✗ Error: {e}")
            results["failed"] += 1
        
        # Test 2: Get specific shop
        logger.info(f"\n2. Testing GET /shops/{shop_id}.json...")
        try:
            async with session.get(f"{base_url}/shops/{shop_id}.json") as response:
                if response.status == 200:
                    shop = await response.json()
                    logger.info(f"   ✓ Shop: {shop.get('title')}")
                    results["passed"] += 1
                else:
                    error = await response.text()
                    logger.error(f"   ✗ Status {response.status}: {error[:200]}")
                    results["failed"] += 1
        except Exception as e:
            logger.error(f"   ✗ Error: {e}")
            results["failed"] += 1
        
        # Test 3: List blueprints
        logger.info("\n3. Testing GET /catalog/blueprints.json...")
        try:
            async with session.get(f"{base_url}/catalog/blueprints.json") as response:
                if response.status == 200:
                    blueprints = await response.json()
                    logger.info(f"   ✓ Found {len(blueprints)} blueprints")
                    results["passed"] += 1
                else:
                    error = await response.text()
                    logger.error(f"   ✗ Status {response.status}: {error[:200]}")
                    results["failed"] += 1
        except Exception as e:
            logger.error(f"   ✗ Error: {e}")
            results["failed"] += 1
        
        # Test 4: Get t-shirt blueprint
        logger.info("\n4. Testing GET /catalog/blueprints/5.json (T-Shirt)...")
        try:
            async with session.get(f"{base_url}/catalog/blueprints/5.json") as response:
                if response.status == 200:
                    bp = await response.json()
                    logger.info(f"   ✓ Blueprint: {bp.get('title')}")
                    results["passed"] += 1
                else:
                    error = await response.text()
                    logger.error(f"   ✗ Status {response.status}: {error[:200]}")
                    results["failed"] += 1
        except Exception as e:
            logger.error(f"   ✗ Error: {e}")
            results["failed"] += 1
        
        # Test 5: Get print providers
        logger.info("\n5. Testing GET /catalog/blueprints/5/print_providers.json...")
        try:
            async with session.get(f"{base_url}/catalog/blueprints/5/print_providers.json") as response:
                if response.status == 200:
                    providers = await response.json()
                    logger.info(f"   ✓ Found {len(providers)} print providers")
                    if providers:
                        provider = providers[0]
                        logger.info(f"     First: {provider.get('title')} (ID: {provider.get('id')})")
                    results["passed"] += 1
                else:
                    error = await response.text()
                    logger.error(f"   ✗ Status {response.status}: {error[:200]}")
                    results["failed"] += 1
        except Exception as e:
            logger.error(f"   ✗ Error: {e}")
            results["failed"] += 1
        
        # Test 6: List products
        logger.info(f"\n6. Testing GET /shops/{shop_id}/products.json...")
        try:
            async with session.get(f"{base_url}/shops/{shop_id}/products.json?limit=5") as response:
                if response.status == 200:
                    result = await response.json()
                    products = result.get("data", result) if isinstance(result, dict) else result
                    count = len(products) if isinstance(products, list) else 0
                    logger.info(f"   ✓ Found {count} product(s)")
                    results["passed"] += 1
                else:
                    error = await response.text()
                    logger.error(f"   ✗ Status {response.status}: {error[:200]}")
                    results["failed"] += 1
        except Exception as e:
            logger.error(f"   ✗ Error: {e}")
            results["failed"] += 1
    
    logger.info("\n" + "=" * 50)
    logger.info(f"Results: {results['passed']} passed, {results['failed']} failed")
    logger.info("=" * 50)
    
    return results["failed"] == 0


def main():
    if len(sys.argv) != 3:
        print("Usage: python scripts/quick_test_printify.py <API_KEY> <SHOP_ID>")
        print("\nExample:")
        print("  python scripts/quick_test_printify.py eyJhbG... 12345678")
        sys.exit(1)
    
    api_key = sys.argv[1]
    shop_id = sys.argv[2]
    
    print("=" * 50)
    print("Printify API Integration Test")
    print("=" * 50)
    print(f"Shop ID: {shop_id}")
    print(f"API Key: {api_key[:10]}...{api_key[-4:]}")
    print()
    
    success = asyncio.run(test_printify(api_key, shop_id))
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
