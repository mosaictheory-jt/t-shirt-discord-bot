"""Discord bot implementation for monitoring and responding to t-shirt requests."""

import logging
from typing import Optional

import discord
from discord.ext import commands

from src.config import settings
from src.services.orchestrator import TShirtOrchestrator

logger = logging.getLogger(__name__)


class TShirtBot(commands.Bot):
    """Discord bot that monitors messages and creates t-shirts on request."""

    def __init__(self):
        """Initialize the bot with necessary intents and settings."""
        intents = discord.Intents.default()
        intents.message_content = True
        intents.guilds = True
        intents.messages = True

        super().__init__(
            command_prefix="!",
            intents=intents,
            help_command=None,
        )

        self.orchestrator = TShirtOrchestrator()
        self.trigger_keywords = settings.trigger_keywords_list

    async def setup_hook(self) -> None:
        """Set up the bot before it starts."""
        logger.info("Setting up bot...")
        await self.orchestrator.initialize()

    async def on_ready(self) -> None:
        """Handle bot ready event."""
        logger.info(f"Bot is ready! Logged in as {self.user}")
        logger.info(f"Bot is in {len(self.guilds)} guilds")
        
        for guild in self.guilds:
            logger.info(f"  - {guild.name} (ID: {guild.id})")

    async def on_message(self, message: discord.Message) -> None:
        """Handle incoming messages."""
        # Ignore messages from the bot itself
        if message.author.bot:
            return

        # Check if message contains trigger keywords
        message_lower = message.content.lower()
        if not any(keyword in message_lower for keyword in self.trigger_keywords):
            return

        logger.info(
            f"Detected t-shirt request from {message.author} in {message.channel}: "
            f"{message.content[:100]}"
        )

        # Show typing indicator while processing
        async with message.channel.typing():
            try:
                # Process the t-shirt request
                result = await self.orchestrator.process_tshirt_request(
                    message.content,
                    user_id=str(message.author.id),
                    username=str(message.author),
                )

                if result.success:
                    # Reply with the t-shirt link and a fun phrase
                    await message.reply(
                        f"{result.response_phrase}\n\n"
                        f"Check out your custom tee: {result.product_url}"
                    )
                    logger.info(
                        f"Successfully created t-shirt for {message.author}: "
                        f"{result.product_url}"
                    )
                else:
                    await message.reply(
                        f"Yo, hit a snag creating your tee: {result.error_message}"
                    )
                    logger.error(
                        f"Failed to create t-shirt for {message.author}: "
                        f"{result.error_message}"
                    )

            except Exception as e:
                logger.error(
                    f"Error processing t-shirt request: {e}",
                    exc_info=True,
                )
                await message.reply(
                    "Oof, something went wrong on my end. Try again later, fam!"
                )

    async def close(self) -> None:
        """Clean up resources before shutting down."""
        logger.info("Shutting down bot...")
        await self.orchestrator.cleanup()
        await super().close()
