"""Main entry point for the Discord T-Shirt Bot."""

import asyncio
import logging

from src.bot.discord_bot import TShirtBot
from src.config import settings

logger = logging.getLogger(__name__)


async def main() -> None:
    """Initialize and run the Discord bot."""
    settings.setup_logging()
    logger.info("Starting Discord T-Shirt Bot...")

    bot = TShirtBot()
    
    try:
        await bot.start(settings.discord_bot_token)
    except KeyboardInterrupt:
        logger.info("Received keyboard interrupt, shutting down...")
    except Exception as e:
        logger.error(f"Fatal error: {e}", exc_info=True)
    finally:
        await bot.close()


if __name__ == "__main__":
    asyncio.run(main())
