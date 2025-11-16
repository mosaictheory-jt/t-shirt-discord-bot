"""Printful API client for creating and managing t-shirt products."""

import logging
from typing import Dict, Optional

import aiohttp
from pydantic import BaseModel

from src.config import settings

logger = logging.getLogger(__name__)


class PrintfulProduct(BaseModel):
    """Printful product information."""

    product_id: int
    variant_id: int
    sync_product_id: Optional[int] = None
    external_id: Optional[str] = None
    name: str
    thumbnail_url: Optional[str] = None
    retail_price: Optional[float] = None
    currency: str = "USD"


class PrintfulClient:
    """Client for interacting with the Printful API."""

    BASE_URL = "https://api.printful.com"

    def __init__(self):
        """Initialize the Printful client."""
        self.api_key = settings.printful_api_key
        self.store_id = settings.printful_store_id
        self.session: Optional[aiohttp.ClientSession] = None

    async def initialize(self) -> None:
        """Initialize the HTTP session."""
        if not self.session:
            self.session = aiohttp.ClientSession(
                headers={
                    "Authorization": f"Bearer {self.api_key}",
                    "Content-Type": "application/json",
                }
            )
            logger.info("Initialized Printful API client")

    async def cleanup(self) -> None:
        """Clean up the HTTP session."""
        if self.session:
            await self.session.close()
            self.session = None
            logger.info("Closed Printful API client session")

    async def create_product(
        self,
        design_image_url: str,
        product_name: str,
        user_id: str,
    ) -> PrintfulProduct:
        """
        Create a new product on Printful with the design.

        Args:
            design_image_url: URL or base64 of the design image
            product_name: Name for the product
            user_id: User ID for tracking

        Returns:
            PrintfulProduct with product details and URL
        """
        if not self.session:
            await self.initialize()

        try:
            # First, upload the design file
            file_id = await self._upload_design_file(design_image_url)

            # Create a sync product (product in Printful store)
            # Using product ID 71 (Unisex Staple T-Shirt | Bella + Canvas 3001)
            product_id = 71
            variant_id = 4012  # White, Size M (most common default)

            sync_product = await self._create_sync_product(
                product_id=product_id,
                variant_id=variant_id,
                file_id=file_id,
                product_name=product_name,
                external_id=f"discord_{user_id}_{hash(product_name)}",
            )

            logger.info(f"Created Printful product: {sync_product}")

            return sync_product

        except Exception as e:
            logger.error(f"Error creating Printful product: {e}", exc_info=True)
            raise

    async def _upload_design_file(self, image_data: str) -> int:
        """
        Upload a design file to Printful.

        Args:
            image_data: Base64 encoded image or URL

        Returns:
            File ID from Printful
        """
        endpoint = f"{self.BASE_URL}/files"

        payload = {
            "url": image_data if image_data.startswith("http") else None,
            "file": image_data if not image_data.startswith("http") else None,
            "type": "default",
        }

        async with self.session.post(endpoint, json=payload) as response:
            response.raise_for_status()
            data = await response.json()
            
            file_id = data["result"]["id"]
            logger.info(f"Uploaded design file, ID: {file_id}")
            return file_id

    async def _create_sync_product(
        self,
        product_id: int,
        variant_id: int,
        file_id: int,
        product_name: str,
        external_id: str,
    ) -> PrintfulProduct:
        """
        Create a sync product in Printful.

        Args:
            product_id: Printful product template ID
            variant_id: Printful variant ID
            file_id: Uploaded file ID
            product_name: Name for the product
            external_id: External reference ID

        Returns:
            PrintfulProduct object
        """
        endpoint = f"{self.BASE_URL}/store/products"
        params = {"store_id": self.store_id}

        payload = {
            "sync_product": {
                "name": product_name,
                "thumbnail": f"https://api.printful.com/files/{file_id}/preview",
            },
            "sync_variants": [
                {
                    "variant_id": variant_id,
                    "retail_price": "29.99",
                    "files": [
                        {
                            "id": file_id,
                            "type": "default",
                        }
                    ],
                }
            ],
        }

        async with self.session.post(endpoint, json=payload, params=params) as response:
            response.raise_for_status()
            data = await response.json()

            result = data["result"]
            sync_product = result["sync_product"]
            sync_variant = result["sync_variants"][0]

            # Generate the store URL
            store_url = f"https://www.printful.com/dashboard/store/products/{sync_product['id']}"

            return PrintfulProduct(
                product_id=product_id,
                variant_id=variant_id,
                sync_product_id=sync_product["id"],
                external_id=external_id,
                name=product_name,
                thumbnail_url=sync_product.get("thumbnail_url"),
                retail_price=float(sync_variant.get("retail_price", 0)),
                currency=sync_variant.get("currency", "USD"),
            )

    async def get_product_info(self, sync_product_id: int) -> Dict:
        """
        Get product information from Printful.

        Args:
            sync_product_id: The sync product ID

        Returns:
            Product information dictionary
        """
        if not self.session:
            await self.initialize()

        endpoint = f"{self.BASE_URL}/store/products/{sync_product_id}"
        params = {"store_id": self.store_id}

        async with self.session.get(endpoint, params=params) as response:
            response.raise_for_status()
            data = await response.json()
            return data["result"]

    async def list_products(self, limit: int = 20, offset: int = 0) -> dict:
        """
        List all products in the Printful store with pagination.

        Args:
            limit: Maximum number of products to return (default: 20, max: 100)
            offset: Offset for pagination (default: 0)

        Returns:
            Dictionary with 'products' list and pagination info
        """
        if not self.session:
            await self.initialize()

        endpoint = f"{self.BASE_URL}/store/products"
        params = {"store_id": self.store_id, "limit": limit, "offset": offset}

        try:
            async with self.session.get(endpoint, params=params) as response:
                if response.status != 200:
                    error_body = await response.text()
                    logger.error(
                        f"Printful API error (status {response.status}): {error_body}"
                    )
                    # Return empty result for graceful degradation
                    return {"products": [], "paging": {}}
                
                data = await response.json()
                
                return {
                    "products": data.get("result", []),
                    "paging": data.get("paging", {}),
                }
        except Exception as e:
            logger.error(f"Failed to list products: {e}", exc_info=True)
            # Return empty result for graceful degradation
            return {"products": [], "paging": {}}

    async def search_products_by_user(self, user_id: str) -> list:
        """
        Search for products created by a specific user.

        Args:
            user_id: Discord user ID

        Returns:
            List of products created by the user
        """
        if not self.session:
            await self.initialize()

        all_products = []
        offset = 0
        limit = 20

        # Fetch all products (Printful doesn't have user-based filtering)
        while True:
            result = await self.list_products(limit=limit, offset=offset)
            products = result["products"]
            
            if not products:
                break

            # Filter products by external_id containing user_id
            user_products = [
                p for p in products
                if p.get("external_id") and user_id in p.get("external_id", "")
            ]
            all_products.extend(user_products)

            # Check if there are more products
            paging = result.get("paging", {})
            if not paging.get("next"):
                break

            offset += limit

        logger.info(f"Found {len(all_products)} products for user {user_id}")
        return all_products

    async def get_all_designs(self) -> list:
        """
        Get all designs ever created in the store.

        Returns:
            List of all products with design information
        """
        if not self.session:
            await self.initialize()

        all_products = []
        offset = 0
        limit = 20

        while True:
            result = await self.list_products(limit=limit, offset=offset)
            products = result["products"]
            
            if not products:
                break

            all_products.extend(products)

            # Check if there are more products
            paging = result.get("paging", {})
            if not paging.get("next"):
                break

            offset += limit

        logger.info(f"Retrieved {len(all_products)} total designs from store")
        return all_products

    async def get_design_stats(self) -> dict:
        """
        Get statistics about all designs in the store.

        Returns:
            Dictionary with design statistics
        """
        products = await self.get_all_designs()

        # Extract user IDs from external_ids
        user_ids = set()
        for product in products:
            external_id = product.get("external_id", "")
            if "discord_" in external_id:
                # Extract user_id from format: discord_userid_hash
                parts = external_id.split("_")
                if len(parts) >= 2:
                    user_ids.add(parts[1])

        return {
            "total_designs": len(products),
            "unique_users": len(user_ids),
            "designs_per_user": len(products) / len(user_ids) if user_ids else 0,
            "latest_design": products[0] if products else None,
        }
