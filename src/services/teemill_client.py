"""Teemill API client for creating and managing t-shirt products."""

import logging
from typing import Dict, Optional, List

import aiohttp
from pydantic import BaseModel

from src.config import settings

logger = logging.getLogger(__name__)


class TeemillProduct(BaseModel):
    """Teemill product information."""

    order_id: Optional[str] = None
    product_id: Optional[str] = None
    variant_id: Optional[str] = None
    external_id: Optional[str] = None
    name: str
    thumbnail_url: Optional[str] = None
    retail_price: Optional[float] = None
    currency: str = "GBP"
    product_url: Optional[str] = None


class TeemillClient:
    """Client for interacting with the Teemill API."""

    BASE_URL = "https://api.teemill.com/v1"

    def __init__(self):
        """Initialize the Teemill client."""
        self.api_key = settings.teemill_api_key
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
            logger.info("Initialized Teemill API client")

    async def cleanup(self) -> None:
        """Clean up the HTTP session."""
        if self.session:
            await self.session.close()
            self.session = None
            logger.info("Closed Teemill API client session")

    async def create_product(
        self,
        design_image_url: str,
        product_name: str,
        user_id: str,
    ) -> TeemillProduct:
        """
        Create a new product order on Teemill with the design.

        Args:
            design_image_url: URL or base64 of the design image
            product_name: Name for the product
            user_id: User ID for tracking

        Returns:
            TeemillProduct with product details and URL
        """
        if not self.session:
            await self.initialize()

        try:
            # Upload the design image first
            image_url = await self._upload_design_image(design_image_url)

            # Create an order with the design
            # Default to organic cotton t-shirt
            order = await self._create_order(
                product_name=product_name,
                image_url=image_url,
                external_id=f"discord_{user_id}_{hash(product_name)}",
            )

            logger.info(f"Created Teemill product: {order}")

            return order

        except Exception as e:
            logger.error(f"Error creating Teemill product: {e}", exc_info=True)
            raise

    async def _upload_design_image(self, image_data: str) -> str:
        """
        Upload a design image to Teemill.

        Args:
            image_data: Base64 encoded image or URL

        Returns:
            URL of the uploaded image
        """
        endpoint = f"{self.BASE_URL}/files"

        # If it's already a URL, return it
        if image_data.startswith("http"):
            return image_data

        # Otherwise, upload the base64 image
        payload = {
            "file": image_data,
            "type": "design",
        }

        async with self.session.post(endpoint, json=payload) as response:
            response.raise_for_status()
            data = await response.json()
            
            image_url = data.get("url") or data.get("file_url")
            logger.info(f"Uploaded design image: {image_url}")
            return image_url

    async def _create_order(
        self,
        product_name: str,
        image_url: str,
        external_id: str,
    ) -> TeemillProduct:
        """
        Create an order in Teemill.

        Args:
            product_name: Name for the product
            image_url: URL of the design image
            external_id: External reference ID

        Returns:
            TeemillProduct object
        """
        endpoint = f"{self.BASE_URL}/orders"

        # Default product configuration for organic cotton t-shirt
        payload = {
            "products": [
                {
                    "product_code": "OTC01",  # Organic Cotton T-Shirt
                    "size": "M",
                    "color": "white",
                    "quantity": 1,
                    "print_areas": {
                        "front": {
                            "image_url": image_url,
                            "position": "center",
                        }
                    },
                }
            ],
            "reference": external_id,
            "metadata": {
                "product_name": product_name,
                "created_by": "discord_bot",
            },
        }

        async with self.session.post(endpoint, json=payload) as response:
            response.raise_for_status()
            data = await response.json()

            order_id = data.get("order_id") or data.get("id")
            product = data.get("products", [{}])[0] if data.get("products") else {}
            
            # Generate product URL
            product_url = data.get("url") or f"https://teemill.com/order/{order_id}"

            return TeemillProduct(
                order_id=order_id,
                product_id=product.get("product_id") or product.get("id"),
                variant_id=product.get("variant_id"),
                external_id=external_id,
                name=product_name,
                thumbnail_url=product.get("thumbnail_url") or image_url,
                retail_price=product.get("price", 25.0),
                currency=product.get("currency", "GBP"),
                product_url=product_url,
            )

    async def get_product_info(self, order_id: str) -> Dict:
        """
        Get order/product information from Teemill.

        Args:
            order_id: The order ID

        Returns:
            Product information dictionary
        """
        if not self.session:
            await self.initialize()

        endpoint = f"{self.BASE_URL}/orders/{order_id}"

        async with self.session.get(endpoint) as response:
            response.raise_for_status()
            data = await response.json()
            return data

    async def list_products(self, limit: int = 20, offset: int = 0) -> dict:
        """
        List all orders/products with pagination.

        Args:
            limit: Maximum number of products to return (default: 20)
            offset: Offset for pagination (default: 0)

        Returns:
            Dictionary with 'products' list and pagination info
        """
        if not self.session:
            await self.initialize()

        endpoint = f"{self.BASE_URL}/orders"
        params = {"limit": limit, "offset": offset}

        try:
            async with self.session.get(endpoint, params=params) as response:
                if response.status != 200:
                    error_body = await response.text()
                    logger.error(
                        f"Teemill API error (status {response.status}): {error_body}"
                    )
                    return {"products": [], "paging": {}}
                
                data = await response.json()
                
                orders = data.get("orders", [])
                
                return {
                    "products": orders,
                    "paging": {
                        "total": data.get("total", len(orders)),
                        "limit": limit,
                        "offset": offset,
                    },
                }
        except Exception as e:
            logger.error(f"Failed to list products: {e}", exc_info=True)
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

        # Fetch all products and filter by user
        while True:
            result = await self.list_products(limit=limit, offset=offset)
            products = result["products"]
            
            if not products:
                break

            # Filter products by reference containing user_id
            user_products = [
                p for p in products
                if p.get("reference") and user_id in p.get("reference", "")
            ]
            all_products.extend(user_products)

            # Check if there are more products
            paging = result.get("paging", {})
            total = paging.get("total", 0)
            if offset + limit >= total:
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
            total = paging.get("total", 0)
            if offset + limit >= total:
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

        # Extract user IDs from references
        user_ids = set()
        for product in products:
            reference = product.get("reference", "")
            if "discord_" in reference:
                # Extract user_id from format: discord_userid_hash
                parts = reference.split("_")
                if len(parts) >= 2:
                    user_ids.add(parts[1])

        return {
            "total_designs": len(products),
            "unique_users": len(user_ids),
            "designs_per_user": len(products) / len(user_ids) if user_ids else 0,
            "latest_design": products[0] if products else None,
        }
