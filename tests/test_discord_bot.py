"""Tests for Discord bot."""

import pytest
from unittest.mock import AsyncMock, MagicMock, patch
import discord

from src.bot.discord_bot import TShirtBot
from src.services.orchestrator import TShirtResult


class TestTShirtBot:
    """Test suite for TShirtBot."""

    @pytest.fixture
    def bot(self):
        """Create a bot instance."""
        return TShirtBot()

    def test_bot_initialization(self, bot):
        """Test bot initializes with correct settings."""
        assert bot.orchestrator is not None
        assert len(bot.trigger_keywords) > 0
        assert "tshirt" in bot.trigger_keywords or "t-shirt" in bot.trigger_keywords

    @pytest.mark.asyncio
    async def test_setup_hook(self, bot):
        """Test bot setup hook."""
        with patch.object(bot.orchestrator, 'initialize', new_callable=AsyncMock) as mock_init:
            await bot.setup_hook()
            mock_init.assert_called_once()

    @pytest.mark.asyncio
    async def test_on_message_ignores_bot_messages(self, bot):
        """Test that bot ignores messages from other bots."""
        # Create a mock message from a bot
        message = MagicMock(spec=discord.Message)
        message.author.bot = True
        message.content = "I want a t-shirt"
        
        # Should return early without processing
        with patch.object(bot.orchestrator, 'process_tshirt_request') as mock_process:
            await bot.on_message(message)
            mock_process.assert_not_called()

    @pytest.mark.asyncio
    async def test_on_message_ignores_without_trigger(self, bot):
        """Test that bot ignores messages without trigger keywords."""
        message = MagicMock(spec=discord.Message)
        message.author.bot = False
        message.content = "Hello world, how are you?"
        
        with patch.object(bot.orchestrator, 'process_tshirt_request') as mock_process:
            await bot.on_message(message)
            mock_process.assert_not_called()

    @pytest.mark.asyncio
    async def test_on_message_processes_with_trigger(self, bot):
        """Test that bot processes messages with trigger keywords."""
        # Create a mock message with trigger keyword
        message = MagicMock(spec=discord.Message)
        message.author.bot = False
        message.author.id = 12345
        message.author.__str__ = MagicMock(return_value="TestUser#1234")
        message.content = "I want a t-shirt that says 'Hello'"
        message.channel = MagicMock()
        message.channel.typing = MagicMock()
        message.channel.typing.return_value.__aenter__ = AsyncMock()
        message.channel.typing.return_value.__aexit__ = AsyncMock()
        message.reply = AsyncMock()
        
        # Mock successful orchestration
        success_result = TShirtResult(
            success=True,
            product_url="https://example.com/product/123",
            response_phrase="Got you fam!",
            phrase="Hello",
        )
        
        with patch.object(
            bot.orchestrator,
            'process_tshirt_request',
            new_callable=AsyncMock,
            return_value=success_result,
        ):
            await bot.on_message(message)
            
            # Verify reply was called
            message.reply.assert_called_once()
            call_args = message.reply.call_args[0][0]
            assert "Got you fam!" in call_args
            assert "https://example.com/product/123" in call_args

    @pytest.mark.asyncio
    async def test_on_message_handles_failure(self, bot):
        """Test that bot handles orchestration failures gracefully."""
        message = MagicMock(spec=discord.Message)
        message.author.bot = False
        message.author.id = 12345
        message.author.__str__ = MagicMock(return_value="TestUser#1234")
        message.content = "I want a shirt that says 'Test'"
        message.channel = MagicMock()
        message.channel.typing = MagicMock()
        message.channel.typing.return_value.__aenter__ = AsyncMock()
        message.channel.typing.return_value.__aexit__ = AsyncMock()
        message.reply = AsyncMock()
        
        # Mock failed orchestration
        failure_result = TShirtResult(
            success=False,
            response_phrase="Hmm",
            error_message="API error",
        )
        
        with patch.object(
            bot.orchestrator,
            'process_tshirt_request',
            new_callable=AsyncMock,
            return_value=failure_result,
        ):
            await bot.on_message(message)
            
            # Verify error reply was called
            message.reply.assert_called_once()
            call_args = message.reply.call_args[0][0]
            assert "snag" in call_args.lower() or "error" in call_args.lower()

    @pytest.mark.asyncio
    async def test_on_message_handles_exception(self, bot):
        """Test that bot handles unexpected exceptions."""
        message = MagicMock(spec=discord.Message)
        message.author.bot = False
        message.author.id = 12345
        message.author.__str__ = MagicMock(return_value="TestUser#1234")
        message.content = "I want a t-shirt"
        message.channel = MagicMock()
        message.channel.typing = MagicMock()
        message.channel.typing.return_value.__aenter__ = AsyncMock()
        message.channel.typing.return_value.__aexit__ = AsyncMock()
        message.reply = AsyncMock()
        
        with patch.object(
            bot.orchestrator,
            'process_tshirt_request',
            new_callable=AsyncMock,
            side_effect=Exception("Unexpected error"),
        ):
            await bot.on_message(message)
            
            # Verify error reply was sent
            message.reply.assert_called_once()
            call_args = message.reply.call_args[0][0]
            assert "wrong" in call_args.lower() or "error" in call_args.lower()

    @pytest.mark.asyncio
    async def test_close(self, bot):
        """Test bot cleanup on close."""
        with patch.object(bot.orchestrator, 'cleanup', new_callable=AsyncMock) as mock_cleanup:
            with patch('discord.ext.commands.Bot.close', new_callable=AsyncMock):
                await bot.close()
                mock_cleanup.assert_called_once()
