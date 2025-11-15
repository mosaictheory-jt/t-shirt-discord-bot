# Quick Start Guide

Get the Discord T-Shirt Bot running in 5 minutes!

## Step 1: Install UV Package Manager

```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

Restart your terminal, then verify:
```bash
uv --version
```

## Step 2: Clone and Install

```bash
# Clone the repository
git clone <repository-url>
cd discord-tshirt-bot

# Install dependencies
uv pip install -r requirements.txt
```

## Step 3: Get API Keys

You need three API keys:

### Discord Bot Token
1. Go to [Discord Developer Portal](https://discord.com/developers/applications)
2. Create "New Application"
3. Go to "Bot" → "Add Bot"
4. Copy the token
5. Enable "Message Content Intent"
6. Invite bot to your server (OAuth2 → URL Generator → bot → permissions)

### Google Gemini API Key
1. Go to [Google AI Studio](https://makersuite.google.com/app/apikey)
2. Click "Create API Key"
3. Copy the key

### Printful API Key
1. Sign up at [Printful](https://www.printful.com/)
2. Create or select a store
3. Go to Settings → API
4. Generate and copy API key

## Step 4: Configure Environment

```bash
# Copy example config
cp .env.example .env

# Edit with your keys
nano .env
```

Add your keys:
```bash
DISCORD_BOT_TOKEN=your_discord_token_here
GOOGLE_API_KEY=your_google_key_here
PRINTFUL_API_KEY=your_printful_key_here
```

## Step 5: Run the Bot

```bash
# Option 1: Direct run
python -m src.main

# Option 2: Use convenience script
./run.sh

# Option 3: Docker
docker-compose up -d
```

## Step 6: Test It!

In your Discord server, type:
```
I want a t-shirt that says "Hello World"
```

The bot should respond with a link to your custom t-shirt!

## Troubleshooting

**Bot doesn't respond?**
- Check Message Content Intent is enabled
- Verify bot has read/send message permissions
- Check your Discord token is correct

**LLM errors?**
- Verify Google API key is valid
- Check your API quota

**Printful errors?**
- Verify Printful API key is correct
- Ensure you have a store set up

## Next Steps

- **Deploy to Cloud**: [Deployment Guide](docs/DEPLOYMENT.md)
- **Run Tests**: `pytest --cov=src`
- **Contribute**: [Contributing Guide](docs/CONTRIBUTING.md)
- **Full Docs**: [Documentation Index](docs/README.md)

---

Need help? Check the [Setup Guide](docs/SETUP.md) or open an issue!
