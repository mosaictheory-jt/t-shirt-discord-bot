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

        async with self.session.post(endpoint, json=payload) as response:
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

        async with self.session.get(endpoint) as response:
            response.raise_for_status()
            data = await response.json()
            return data["result"]

    async def list_products(self) -> list:
        """
        List all products in the Printful store.

        Returns:
            List of products
        """
        if not self.session:
            await self.initialize()

        endpoint = f"{self.BASE_URL}/store/products"

        async with self.session.get(endpoint) as response:
            response.raise_for_status()
            data = await response.json()
            return data["result"]
