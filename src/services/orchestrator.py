"""Main orchestrator for coordinating t-shirt creation workflow."""

import base64
import logging
import random
from pathlib import Path
from typing import Optional

from pydantic import BaseModel

from src.services.design_generator import DesignGenerator
from src.services.llm_parser import LLMParser
from src.services.teemill_client import TeemillClient

logger = logging.getLogger(__name__)


class TShirtResult(BaseModel):
    """Result of a t-shirt creation request."""

    success: bool
    product_url: Optional[str] = None
    response_phrase: str
    error_message: Optional[str] = None
    phrase: Optional[str] = None


class TShirtOrchestrator:
    """Orchestrates the full t-shirt creation workflow."""

    # Fun response phrases
    RESPONSE_PHRASES = [
        "Got you fam! 🔥",
        "Say less, squad! 💪",
        "Bet! Your fit is ready! 👕",
        "No cap, this tee slaps! 🎯",
        "It's giving main character energy! ✨",
        "Chef's kiss on this one! 👨‍🍳💋",
        "Your drip has arrived! 💧",
        "Sheesh, this goes hard! 🔥",
        "We understood the assignment! 📝✅",
        "Straight bussin'! 💯",
    ]

    def __init__(self):
        """Initialize the orchestrator with all services."""
        self.llm_parser = LLMParser()
        self.design_generator = DesignGenerator()
        self.teemill_client = TeemillClient()

    async def initialize(self) -> None:
        """Initialize all services."""
        await self.teemill_client.initialize()
        logger.info("Orchestrator initialized")

    async def cleanup(self) -> None:
        """Clean up all services."""
        await self.teemill_client.cleanup()
        logger.info("Orchestrator cleaned up")

    async def get_user_designs(self, user_id: str) -> list:
        """
        Get all designs created by a specific user.

        Args:
            user_id: The Discord user ID

        Returns:
            List of designs created by the user
        """
        try:
            designs = await self.teemill_client.search_products_by_user(user_id)
            logger.info(f"Retrieved {len(designs)} designs for user {user_id}")
            return designs
        except Exception as e:
            logger.error(f"Error retrieving user designs: {e}", exc_info=True)
            return []

    async def get_design_statistics(self) -> dict:
        """
        Get statistics about all designs in the store.

        Returns:
            Dictionary with design statistics
        """
        try:
            stats = await self.teemill_client.get_design_stats()
            logger.info(f"Design stats: {stats['total_designs']} total designs")
            return stats
        except Exception as e:
            logger.error(f"Error retrieving design stats: {e}", exc_info=True)
            return {
                "total_designs": 0,
                "unique_users": 0,
                "designs_per_user": 0,
                "latest_design": None,
            }

    async def get_all_designs(self) -> list:
        """
        Get all designs ever created.

        Returns:
            List of all designs
        """
        try:
            designs = await self.teemill_client.get_all_designs()
            logger.info(f"Retrieved {len(designs)} total designs")
            return designs
        except Exception as e:
            logger.error(f"Error retrieving all designs: {e}", exc_info=True)
            return []

    async def process_tshirt_request(
        self,
        message: str,
        user_id: str,
        username: str,
    ) -> TShirtResult:
        """
        Process a t-shirt request end-to-end.

        Args:
            message: The user's message requesting a t-shirt
            user_id: The Discord user ID
            username: The Discord username

        Returns:
            TShirtResult with success status and product URL
        """
        try:
            logger.info(f"Processing t-shirt request for user {username}")

            # Step 1: Parse the message to extract design details
            request = await self.llm_parser.parse_message(message)
            
            if not request:
                return TShirtResult(
                    success=False,
                    response_phrase="Hmm, couldn't quite catch that...",
                    error_message="Failed to parse message",
                )

            logger.info(f"Parsed request: {request}")

            # Step 2: Generate the design image
            design_path, design_bytes = await self.design_generator.generate_design(
                request
            )

            logger.info(f"Generated design at {design_path}")

            # Step 3: Upload to Teemill and create product
            # Convert image to base64 for upload
            design_base64 = base64.b64encode(design_bytes).decode("utf-8")

            product = await self.teemill_client.create_product(
                design_image_url=f"data:image/png;base64,{design_base64}",
                product_name=f"{request.phrase[:50]} - Custom Tee",
                user_id=user_id,
            )

            logger.info(f"Created Teemill product: {product.order_id}")

            # Use the product URL from Teemill
            product_url = product.product_url or f"https://teemill.com/order/{product.order_id}"

            # Step 4: Return success with a fun phrase
            response_phrase = random.choice(self.RESPONSE_PHRASES)

            return TShirtResult(
                success=True,
                product_url=product_url,
                response_phrase=response_phrase,
                phrase=request.phrase,
            )

        except Exception as e:
            logger.error(f"Error in orchestration: {e}", exc_info=True)
            return TShirtResult(
                success=False,
                response_phrase="Oof, something broke on our end!",
                error_message=str(e),
            )
