# Setup Guide

This guide will walk you through setting up the Discord T-Shirt Bot.

## Prerequisites

- Python 3.11 or higher
- UV package manager
- Discord Bot Token
- Google API Key (for Gemini)
- Printful API Key
- (Optional) Langsmith API Key for tracing

## Installation

### 1. Install UV Package Manager

```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

### 2. Clone the Repository

```bash
git clone <repository-url>
cd discord-tshirt-bot
```

### 3. Install Dependencies

```bash
uv pip install -e .
```

### 4. Set Up Environment Variables

Copy the example environment file:

```bash
cp .env.example .env
```

Edit `.env` and fill in your credentials:

```bash
# Discord Configuration
DISCORD_BOT_TOKEN=your_discord_bot_token_here
DISCORD_GUILD_IDS=123456789,987654321

# Google Gemini API
GOOGLE_API_KEY=your_google_api_key_here

# Langsmith Configuration (optional)
LANGCHAIN_API_KEY=your_langsmith_api_key_here
LANGCHAIN_TRACING_V2=true
LANGCHAIN_PROJECT=discord-tshirt-bot

# Printful API
PRINTFUL_API_KEY=your_printful_api_key_here

# Bot Configuration
BOT_TRIGGER_KEYWORDS=tshirt,t-shirt,shirt,merch
BOT_LOG_LEVEL=INFO
```

## Getting API Keys

### Discord Bot Token

1. Go to [Discord Developer Portal](https://discord.com/developers/applications)
2. Click "New Application" and give it a name
3. Go to the "Bot" section
4. Click "Add Bot"
5. Under "Token", click "Copy" to get your bot token
6. Enable the following Privileged Gateway Intents:
   - Message Content Intent
   - Server Members Intent (optional)
7. Go to OAuth2 > URL Generator
8. Select scopes: `bot`
9. Select permissions: 
   - Read Messages/View Channels
   - Send Messages
   - Read Message History
10. Copy the generated URL and use it to invite the bot to your server

### Google API Key (Gemini)

1. Go to [Google AI Studio](https://makersuite.google.com/app/apikey)
2. Click "Create API Key"
3. Copy the generated API key

### Printful API Key

1. Go to [Printful](https://www.printful.com/)
2. Sign up or log in
3. Go to Settings > Stores
4. Create a new store or select an existing one
5. Go to Settings > API
6. Generate an API key
7. Copy the key

### Langsmith API Key (Optional)

1. Go to [Langsmith](https://smith.langchain.com/)
2. Sign up or log in
3. Go to Settings > API Keys
4. Create a new API key
5. Copy the key

## Running the Bot

### Local Development

```bash
python -m src.main
```

### Using Docker

Build and run with Docker Compose:

```bash
docker-compose up -d
```

View logs:

```bash
docker-compose logs -f
```

Stop the bot:

```bash
docker-compose down
```

## Testing

Once the bot is running, test it in your Discord server:

1. **Create a design**: Type "I want a t-shirt that says 'Code is Life'"
2. The bot should respond with a link to your custom t-shirt
3. **View your history**: Type `!mydesigns` to see all your past designs
4. Check the logs for any errors

## Bot Commands

The bot responds to the following commands:

### `!mydesigns`
View all t-shirt designs you've created.

**Example:**
```
User: !mydesigns
Bot: Your Design History (2 designs):
     1. Code is Life - Custom Tee
        🔗 View: https://www.printful.com/dashboard/store/products/12345
     2. Hello World - Custom Tee
        🔗 View: https://www.printful.com/dashboard/store/products/12346
```

### Natural Language Requests
Simply mention a t-shirt in your message with trigger keywords:
- "I want a t-shirt that says..."
- "Make me a shirt with..."
- "Can I get merch that says..."

See **[Design Tracking Guide](DESIGN_TRACKING.md)** for more information about viewing and managing your designs.

## Troubleshooting

### Bot doesn't respond to messages

- Make sure the bot has the "Message Content Intent" enabled in Discord Developer Portal
- Check that the bot has permissions to read and send messages in the channel
- Verify your `DISCORD_BOT_TOKEN` is correct

### LLM parsing errors

- Verify your `GOOGLE_API_KEY` is valid
- Check your Google Cloud quota
- Review logs for specific error messages

### Printful API errors

- Verify your `PRINTFUL_API_KEY` is valid
- Make sure you have a Printful store set up
- Check Printful API rate limits

### Image generation issues

- Ensure the system has font files available
- Check file permissions on the `generated_images` directory
- Review logs for PIL/Pillow errors
