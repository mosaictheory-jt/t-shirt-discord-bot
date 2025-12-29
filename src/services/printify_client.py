"""Printify API client for creating and managing t-shirt products."""

import logging
from typing import Dict, Optional, List

import aiohttp
from pydantic import BaseModel

from src.config import settings

logger = logging.getLogger(__name__)


class PrintifyProduct(BaseModel):
    """Printify product information."""

    product_id: Optional[str] = None
    title: str
    description: Optional[str] = None
    blueprint_id: Optional[int] = None
    print_provider_id: Optional[int] = None
    variant_id: Optional[int] = None
    external_id: Optional[str] = None
    thumbnail_url: Optional[str] = None
    retail_price: Optional[float] = None
    currency: str = "USD"
    product_url: Optional[str] = None
    is_visible: bool = False  # Whether product is visible/published


class PrintifyClient:
    """Client for interacting with the Printify API."""

    BASE_URL = "https://api.printify.com/v1"

    # Common blueprint IDs (these are standard across Printify)
    BLUEPRINT_UNISEX_TSHIRT = 5  # Unisex Heavy Cotton Tee (Gildan 5000)
    BLUEPRINT_BELLA_CANVAS = 6  # Bella+Canvas 3001 Unisex Jersey
    
    # Print provider IDs (varies by region and availability)
    # These are common US-based providers
    PRINT_PROVIDER_MONSTER_DIGITAL = 99
    PRINT_PROVIDER_DUPLIUM = 28
    PRINT_PROVIDER_AWKWARD_STYLES = 29
    
    # Default print provider - will auto-detect if not available
    DEFAULT_PRINT_PROVIDER_ID = None  # Auto-detect first available

    def __init__(self):
        """Initialize the Printify client."""
        self.api_key = settings.printify_api_key
        self.shop_id = settings.printify_shop_id
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
            logger.info("Initialized Printify API client")

    async def verify_connection(self) -> bool:
        """
        Verify API connection and credentials.

        Returns:
            True if connection is valid, False otherwise
        """
        if not self.session:
            await self.initialize()

        try:
            endpoint = f"{self.BASE_URL}/shops.json"
            async with self.session.get(endpoint) as response:
                if response.status == 200:
                    shops = await response.json()
                    logger.info(f"API connection verified. Found {len(shops)} shop(s)")
                    return True
                else:
                    error = await response.text()
                    logger.error(f"API verification failed (status {response.status}): {error}")
                    return False
        except Exception as e:
            logger.error(f"API connection error: {e}")
            return False

    async def get_shops(self) -> List[Dict]:
        """
        Get all shops for the account.

        Returns:
            List of shop dictionaries
        """
        if not self.session:
            await self.initialize()

        endpoint = f"{self.BASE_URL}/shops.json"
        async with self.session.get(endpoint) as response:
            response.raise_for_status()
            return await response.json()

    async def cleanup(self) -> None:
        """Clean up the HTTP session."""
        if self.session:
            await self.session.close()
            self.session = None
            logger.info("Closed Printify API client session")

    async def create_product(
        self,
        design_image_url: str,
        product_name: str,
        user_id: str,
        blueprint_id: int = BLUEPRINT_UNISEX_TSHIRT,
        print_provider_id: Optional[int] = None,
    ) -> PrintifyProduct:
        """
        Create a new product on Printify with the design.

        Args:
            design_image_url: URL or base64 of the design image
            product_name: Name for the product
            user_id: User ID for tracking
            blueprint_id: Printify blueprint ID (default: unisex t-shirt)
            print_provider_id: Print provider ID (default: auto-detect first available)

        Returns:
            PrintifyProduct with product details and URL
        """
        if not self.session:
            await self.initialize()

        try:
            # Auto-detect print provider if not specified
            if print_provider_id is None:
                providers = await self.get_print_providers(blueprint_id)
                if not providers:
                    raise ValueError(f"No print providers available for blueprint {blueprint_id}")
                print_provider_id = providers[0]["id"]
                logger.info(f"Auto-selected print provider: {providers[0].get('title')} (ID: {print_provider_id})")

            # Upload the design image first
            image_id = await self._upload_design_image(design_image_url, product_name)

            # Get the blueprint details to find available variants and print areas
            blueprint = await self._get_blueprint(blueprint_id, print_provider_id)

            # Create the product with the design
            product = await self._create_product(
                product_name=product_name,
                description=f"Custom design created by user {user_id}",
                blueprint_id=blueprint_id,
                print_provider_id=print_provider_id,
                image_id=image_id,
                external_id=f"discord_{user_id}_{hash(product_name)}",
                blueprint=blueprint,
            )

            logger.info(f"Created Printify product: {product.product_id}")

            return product

        except Exception as e:
            logger.error(f"Error creating Printify product: {e}", exc_info=True)
            raise

    async def _upload_design_image(self, image_data: str, file_name: str) -> str:
        """
        Upload a design image to Printify.

        Args:
            image_data: Base64 encoded image or URL
            file_name: Name for the uploaded file

        Returns:
            Image ID from Printify
        """
        endpoint = f"{self.BASE_URL}/uploads/images.json"

        # If it's a URL, use URL upload
        if image_data.startswith("http"):
            payload = {
                "file_name": f"{file_name}.png",
                "url": image_data,
            }
        else:
            # For base64, extract the actual base64 data
            if "base64," in image_data:
                image_data = image_data.split("base64,")[1]
            
            payload = {
                "file_name": f"{file_name}.png",
                "contents": image_data,
            }

        async with self.session.post(endpoint, json=payload) as response:
            response.raise_for_status()
            data = await response.json()
            
            image_id = data.get("id")
            logger.info(f"Uploaded design image: {image_id}")
            return image_id

    async def get_print_providers(self, blueprint_id: int) -> List[Dict]:
        """
        Get available print providers for a blueprint.

        Args:
            blueprint_id: The blueprint ID

        Returns:
            List of print provider dictionaries
        """
        if not self.session:
            await self.initialize()

        endpoint = f"{self.BASE_URL}/catalog/blueprints/{blueprint_id}/print_providers.json"

        async with self.session.get(endpoint) as response:
            response.raise_for_status()
            data = await response.json()
            logger.info(f"Found {len(data)} print providers for blueprint {blueprint_id}")
            return data

    async def _get_blueprint(self, blueprint_id: int, print_provider_id: int) -> Dict:
        """
        Get blueprint details including variants and print areas.

        Args:
            blueprint_id: The blueprint ID
            print_provider_id: The print provider ID

        Returns:
            Blueprint details dictionary
        """
        endpoint = f"{self.BASE_URL}/catalog/blueprints/{blueprint_id}/print_providers/{print_provider_id}/variants.json"

        async with self.session.get(endpoint) as response:
            response.raise_for_status()
            data = await response.json()
            return data

    async def _get_print_areas(self, blueprint_id: int, print_provider_id: int) -> List[Dict]:
        """
        Get available print areas for a blueprint and provider.

        Args:
            blueprint_id: The blueprint ID
            print_provider_id: The print provider ID

        Returns:
            List of print area dictionaries
        """
        endpoint = f"{self.BASE_URL}/catalog/blueprints/{blueprint_id}/print_providers/{print_provider_id}/printing.json"

        async with self.session.get(endpoint) as response:
            response.raise_for_status()
            data = await response.json()
            return data.get("placeholders", [])

    async def _create_product(
        self,
        product_name: str,
        description: str,
        blueprint_id: int,
        print_provider_id: int,
        image_id: str,
        external_id: str,
        blueprint: Dict,
    ) -> PrintifyProduct:
        """
        Create a product in Printify.

        Args:
            product_name: Name for the product
            description: Product description
            blueprint_id: Printify blueprint ID
            print_provider_id: Print provider ID
            image_id: ID of the uploaded image
            external_id: External reference ID
            blueprint: Blueprint details with variants

        Returns:
            PrintifyProduct object
        """
        endpoint = f"{self.BASE_URL}/shops/{self.shop_id}/products.json"

        # Get the variants from the blueprint data
        variants = blueprint.get("variants", [])
        if not variants:
            raise ValueError("No variants available for this blueprint")

        # Select first 3 variants (common sizes: S, M, L)
        selected_variants = variants[:3]
        variant_ids = [v["id"] for v in selected_variants]

        # Create print areas configuration - place image on front
        print_areas_config = [
            {
                "variant_ids": variant_ids,
                "placeholders": [
                    {
                        "position": "front",
                        "images": [
                            {
                                "id": image_id,
                                "x": 0.5,  # Center horizontally
                                "y": 0.5,  # Center vertically
                                "scale": 1.0,
                                "angle": 0,
                            }
                        ]
                    }
                ]
            }
        ]

        payload = {
            "title": product_name,
            "description": description,
            "blueprint_id": blueprint_id,
            "print_provider_id": print_provider_id,
            "variants": [
                {
                    "id": v["id"],
                    "price": 2500,  # $25.00 in cents
                    "is_enabled": True,
                }
                for v in selected_variants
            ],
            "print_areas": print_areas_config,
        }

        async with self.session.post(endpoint, json=payload) as response:
            if response.status != 200:
                error_body = await response.text()
                logger.error(f"Product creation failed ({response.status}): {error_body}")
                response.raise_for_status()
            
            data = await response.json()
            product_id = data.get("id")
            
            # Get the first variant for details
            product_variants = data.get("variants", [])
            first_variant = product_variants[0] if product_variants else {}
            
            # Get thumbnail from images
            images = data.get("images", [])
            thumbnail_url = images[0].get("src") if images else None

            return PrintifyProduct(
                product_id=product_id,
                title=product_name,
                description=description,
                blueprint_id=blueprint_id,
                print_provider_id=print_provider_id,
                variant_id=first_variant.get("id"),
                external_id=external_id,
                thumbnail_url=thumbnail_url,
                retail_price=25.0,  # Default price
                currency="USD",
                product_url=f"https://printify.com/app/products/{product_id}",
                is_visible=data.get("visible", False),
            )

    async def publish_product(self, product_id: str) -> Dict:
        """
        Publish a product to make it available for sale.

        Args:
            product_id: The product ID to publish

        Returns:
            Publishing result
        """
        if not self.session:
            await self.initialize()

        endpoint = f"{self.BASE_URL}/shops/{self.shop_id}/products/{product_id}/publish.json"

        payload = {
            "title": True,  # Publish with current title
            "description": True,
            "images": True,
            "variants": True,
            "tags": True,
        }

        async with self.session.post(endpoint, json=payload) as response:
            response.raise_for_status()
            data = await response.json()
            return data

    async def get_product_info(self, product_id: str) -> Dict:
        """
        Get product information from Printify.

        Args:
            product_id: The product ID

        Returns:
            Product information dictionary
        """
        if not self.session:
            await self.initialize()

        endpoint = f"{self.BASE_URL}/shops/{self.shop_id}/products/{product_id}.json"

        async with self.session.get(endpoint) as response:
            response.raise_for_status()
            data = await response.json()
            return data

    async def delete_product(self, product_id: str) -> bool:
        """
        Delete a product from the shop.

        Args:
            product_id: The product ID to delete

        Returns:
            True if deleted successfully
        """
        if not self.session:
            await self.initialize()

        endpoint = f"{self.BASE_URL}/shops/{self.shop_id}/products/{product_id}.json"

        try:
            async with self.session.delete(endpoint) as response:
                if response.status == 200:
                    logger.info(f"Deleted product: {product_id}")
                    return True
                else:
                    error = await response.text()
                    logger.error(f"Failed to delete product {product_id}: {error}")
                    return False
        except Exception as e:
            logger.error(f"Error deleting product {product_id}: {e}")
            return False

    async def list_products(self, limit: int = 20, page: int = 1) -> dict:
        """
        List all products with pagination.

        Args:
            limit: Maximum number of products to return (default: 20)
            page: Page number for pagination (default: 1)

        Returns:
            Dictionary with 'products' list and pagination info
        """
        if not self.session:
            await self.initialize()

        endpoint = f"{self.BASE_URL}/shops/{self.shop_id}/products.json"
        params = {"limit": limit, "page": page}

        try:
            async with self.session.get(endpoint, params=params) as response:
                if response.status != 200:
                    error_body = await response.text()
                    logger.error(
                        f"Printify API error (status {response.status}): {error_body}"
                    )
                    return {"products": [], "paging": {}}
                
                data = await response.json()
                
                # Printify returns a list directly or wrapped in 'data'
                products = data if isinstance(data, list) else data.get("data", [])
                
                return {
                    "products": products,
                    "paging": {
                        "current_page": page,
                        "limit": limit,
                        "total": len(products),
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
        page = 1
        limit = 20

        # Fetch all products and filter by user
        while True:
            result = await self.list_products(limit=limit, page=page)
            products = result["products"]
            
            if not products:
                break

            # Filter products by external.id containing user_id
            user_products = [
                p for p in products
                if p.get("external", {}).get("id") and user_id in p.get("external", {}).get("id", "")
            ]
            all_products.extend(user_products)

            # Check if there are more products (if we got less than limit, we're done)
            if len(products) < limit:
                break

            page += 1

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
        page = 1
        limit = 20

        while True:
            result = await self.list_products(limit=limit, page=page)
            products = result["products"]
            
            if not products:
                break

            all_products.extend(products)

            # If we got less than limit, we've reached the end
            if len(products) < limit:
                break

            page += 1

        logger.info(f"Retrieved {len(all_products)} total designs from store")
        return all_products

    async def get_design_stats(self) -> dict:
        """
        Get statistics about all designs in the store.

        Returns:
            Dictionary with design statistics
        """
        products = await self.get_all_designs()

        # Extract user IDs from external IDs
        user_ids = set()
        for product in products:
            external_id = product.get("external", {}).get("id", "")
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
