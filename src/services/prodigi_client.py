"""Prodigi Print API client for creating and managing print-on-demand products."""

import logging
from typing import Dict, Optional, List

import aiohttp
from pydantic import BaseModel

from src.config import settings

logger = logging.getLogger(__name__)


class ProdigiProduct(BaseModel):
    """Prodigi product information."""

    order_id: Optional[str] = None
    product_id: Optional[str] = None
    sku: Optional[str] = None
    external_id: Optional[str] = None
    name: str
    thumbnail_url: Optional[str] = None
    retail_price: Optional[float] = None
    currency: str = "USD"
    product_url: Optional[str] = None
    status: Optional[str] = None


class ProdigiClient:
    """Client for interacting with the Prodigi Print API."""

    BASE_URL = "https://api.prodigi.com/v4.0"

    def __init__(self):
        """Initialize the Prodigi client."""
        self.api_key = settings.prodigi_api_key
        self.session: Optional[aiohttp.ClientSession] = None

    async def initialize(self) -> None:
        """Initialize the HTTP session."""
        if not self.session:
            self.session = aiohttp.ClientSession(
                headers={
                    "X-API-Key": self.api_key,
                    "Content-Type": "application/json",
                }
            )
            logger.info("Initialized Prodigi API client")

    async def cleanup(self) -> None:
        """Clean up the HTTP session."""
        if self.session:
            await self.session.close()
            self.session = None
            logger.info("Closed Prodigi API client session")

    async def create_product(
        self,
        design_image_url: str,
        product_name: str,
        user_id: str,
    ) -> ProdigiProduct:
        """
        Create a new product order on Prodigi with the design.

        Args:
            design_image_url: URL or base64 of the design image
            product_name: Name for the product
            user_id: User ID for tracking

        Returns:
            ProdigiProduct with product details and URL
        """
        if not self.session:
            await self.initialize()

        try:
            # Upload the design image first if needed
            image_url = await self._upload_design_image(design_image_url)

            # Create an order with the design
            # Default to unisex t-shirt (SKU: GLOBAL-TSHU-CLAS-MENS)
            order = await self._create_order(
                product_name=product_name,
                image_url=image_url,
                external_id=f"discord_{user_id}_{hash(product_name)}",
            )

            logger.info(f"Created Prodigi product: {order}")

            return order

        except Exception as e:
            logger.error(f"Error creating Prodigi product: {e}", exc_info=True)
            raise

    async def _upload_design_image(self, image_data: str) -> str:
        """
        Upload a design image to Prodigi or return URL.

        Args:
            image_data: Base64 encoded image or URL

        Returns:
            URL of the image
        """
        # If it's already a URL, return it
        if image_data.startswith("http"):
            return image_data

        # For base64 images, Prodigi accepts them directly in the order
        # We'll return the data as-is and handle it in the order creation
        return image_data

    async def _create_order(
        self,
        product_name: str,
        image_url: str,
        external_id: str,
    ) -> ProdigiProduct:
        """
        Create an order in Prodigi.

        Args:
            product_name: Name for the product
            image_url: URL or base64 of the design image
            external_id: External reference ID

        Returns:
            ProdigiProduct object
        """
        endpoint = f"{self.BASE_URL}/Orders"

        # Default product configuration for unisex t-shirt
        # Using standard Prodigi SKU for classic unisex t-shirt
        payload = {
            "merchantReference": external_id,
            "shippingMethod": "Budget",
            "idempotencyKey": external_id,
            "recipient": {
                "name": "Print on Demand",
                "email": "noreply@example.com",
                "address": {
                    "line1": "14 Tottenham Court Road",
                    "line2": "",
                    "postalOrZipCode": "W1T 1JY",
                    "countryCode": "GB",
                    "townOrCity": "London"
                }
            },
            "items": [
                {
                    "merchantReference": external_id,
                    "sku": "GLOBAL-TSHU-CLAS-MENS-MEDI-WHIT",  # Classic unisex white t-shirt, medium
                    "copies": 1,
                    "sizing": "fillPrintArea",
                    "attributes": {
                        "color": "White"
                    },
                    "assets": [
                        {
                            "printArea": "front",
                            "url": image_url if image_url.startswith("http") else None,
                            "md5Hash": None
                        }
                    ]
                }
            ],
            "metadata": {
                "product_name": product_name,
                "created_by": "discord_bot",
            }
        }

        # If using base64, add it to the asset
        if not image_url.startswith("http"):
            payload["items"][0]["assets"][0]["url"] = image_url

        async with self.session.post(endpoint, json=payload) as response:
            response.raise_for_status()
            data = await response.json()

            order_id = data.get("order", {}).get("id") or data.get("id")
            items = data.get("order", {}).get("items", [])
            item = items[0] if items else {}
            
            # Prodigi doesn't provide a direct product URL for preview
            # Orders are for fulfillment, not e-commerce
            product_url = f"https://dashboard.prodigi.com/orders/{order_id}"

            return ProdigiProduct(
                order_id=order_id,
                product_id=item.get("id"),
                sku=item.get("sku"),
                external_id=external_id,
                name=product_name,
                thumbnail_url=None,  # Prodigi doesn't provide thumbnails in API response
                retail_price=item.get("cost", {}).get("amount", 15.0),
                currency=item.get("cost", {}).get("currency", "USD"),
                product_url=product_url,
                status=data.get("order", {}).get("status", {}).get("stage"),
            )

    async def get_product_info(self, order_id: str) -> Dict:
        """
        Get order/product information from Prodigi.

        Args:
            order_id: The order ID

        Returns:
            Product information dictionary
        """
        if not self.session:
            await self.initialize()

        endpoint = f"{self.BASE_URL}/Orders/{order_id}"

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

        endpoint = f"{self.BASE_URL}/Orders"
        params = {"top": limit, "skip": offset}

        try:
            async with self.session.get(endpoint, params=params) as response:
                if response.status != 200:
                    error_body = await response.text()
                    logger.error(
                        f"Prodigi API error (status {response.status}): {error_body}"
                    )
                    return {"products": [], "paging": {}}
                
                data = await response.json()
                
                orders = data.get("orders", [])
                
                return {
                    "products": orders,
                    "paging": {
                        "total": len(orders),  # Prodigi doesn't return total count
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

            # Filter products by merchantReference containing user_id
            user_products = [
                p for p in products
                if p.get("merchantReference") and user_id in p.get("merchantReference", "")
            ]
            all_products.extend(user_products)

            # Prodigi doesn't provide total count, so we fetch until no more results
            if len(products) < limit:
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

            # Fetch until no more results
            if len(products) < limit:
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

        # Extract user IDs from merchantReference
        user_ids = set()
        for product in products:
            reference = product.get("merchantReference", "")
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
