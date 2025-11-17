# Discord T-Shirt Bot 👕🤖

An intelligent Discord bot that automatically creates custom t-shirts based on user messages. Simply mention that you want a t-shirt with a specific phrase, and the bot will generate a design, create a product on Prodigi, and send you an order link!

## ✨ Features

- 🎨 **AI-Powered Design Parsing**: Uses Google Gemini to understand natural language requests
- 🖼️ **Automatic Design Generation**: Creates print-ready t-shirt designs with custom text
- 🛍️ **Print-on-Demand Integration**: Automatically creates products on Prodigi for global fulfillment
- 📜 **Design History Tracking**: All designs tracked in Prodigi dashboard, viewable with `!mydesigns`
- 💬 **Natural Conversation**: Responds with fun, engaging phrases
- 🚀 **Cloud-Ready**: Easily deployable to Google Cloud Platform
- 📊 **Observable**: Optional Langsmith integration for LLM tracing and monitoring
- 🎯 **Customizable**: Configurable trigger keywords, styles, and responses

## 🎬 Quick Start

**Get started in 5 minutes!** See [QUICK_START.md](QUICK_START.md) for detailed instructions.

### TL;DR

```bash
# 1. Install UV
curl -LsSf https://astral.sh/uv/install.sh | sh

# 2. Clone and install
git clone <repository-url>
cd discord-tshirt-bot
uv pip install -r requirements.txt

# 3. Configure
cp .env.example .env
# Edit .env with your API keys

# 4. Run
python -m src.main
```

Get your API keys:
- **Discord**: [Developer Portal](https://discord.com/developers/applications)
- **Google Gemini**: [AI Studio](https://makersuite.google.com/app/apikey)
- **Prodigi**: [Dashboard](https://dashboard.prodigi.com/)

## 📖 Documentation

- **[Documentation Index](docs/README.md)** - Complete documentation overview
- **[Setup Guide](docs/SETUP.md)** - Installation and configuration
- **[Deployment Guide](docs/DEPLOYMENT.md)** - Google Cloud Run deployment
- **[Architecture](docs/ARCHITECTURE.md)** - System design and components
- **[API Reference](docs/API_REFERENCE.md)** - Complete API documentation
- **[Testing Guide](docs/TESTING.md)** - Testing and development
- **[Contributing](docs/CONTRIBUTING.md)** - How to contribute

## 🔧 How It Works

1. **User sends a message** in Discord: "I want a t-shirt that says 'Hello World'"
2. **Bot detects the request** using trigger keywords (t-shirt, shirt, merch, etc.)
3. **Gemini LLM parses the message** to extract:
   - The phrase to print
   - Desired style (modern, retro, graffiti, etc.)
   - Color preferences
   - Whether images are wanted
4. **Design generator creates** a high-resolution PNG image (4500x5400px)
5. **Prodigi API integration**:
   - Uploads the design
   - Creates a print-on-demand order
   - Generates an order URL
6. **Bot replies** with a fun phrase and the order link!

## 🏗️ Project Structure

```
discord-tshirt-bot/
├── src/
│   ├── bot/
│   │   └── discord_bot.py         # Discord bot implementation
│   ├── services/
│   │   ├── llm_parser.py          # Gemini-based message parser
│   │   ├── design_generator.py    # T-shirt design generator
│   │   ├── prodigi_client.py      # Prodigi Print API client
│   │   └── orchestrator.py        # Workflow coordinator
│   ├── config.py                  # Configuration management
│   └── main.py                    # Entry point
├── docs/
│   ├── SETUP.md                   # Setup instructions
│   ├── DEPLOYMENT.md              # Deployment guide
│   ├── ARCHITECTURE.md            # Architecture documentation
│   └── API_REFERENCE.md           # API documentation
├── pyproject.toml                 # UV dependencies
├── Dockerfile                     # Docker container definition
├── docker-compose.yml             # Docker Compose configuration
├── cloudbuild.yaml               # Google Cloud Build config
├── deploy.sh                     # Deployment script
├── run.sh                        # Local development script
└── README.md                     # This file
```

## 🎨 Example Usage

### Creating a T-Shirt

**User in Discord:**
> "I need a cool retro shirt that says 'Born in the 80s'"

**Bot responds:**
> "Got you fam! 🔥
> 
> Check out your custom tee: https://www.printful.com/dashboard/store/products/12345"

### Viewing Design History

**User in Discord:**
> "!mydesigns"

**Bot responds:**
> **Your Design History** (3 designs):
> 
> 1. Born in the 80s - Custom Tee
>    🔗 View: https://www.printful.com/dashboard/store/products/12345
> 
> 2. Code is Life - Custom Tee
>    🔗 View: https://www.printful.com/dashboard/store/products/12346
> 
> 3. Coffee First - Custom Tee
>    🔗 View: https://www.printful.com/dashboard/store/products/12347

## 🌟 Key Technologies

- **Discord.py**: Discord API integration
- **LangChain**: LLM orchestration framework
- **Google Gemini 2.5 Flash**: Advanced language understanding
- **Pillow (PIL)**: Image generation and processing
- **Printful API**: Print-on-demand fulfillment
- **Pydantic**: Data validation and settings management
- **Docker**: Containerization
- **Google Cloud**: Deployment platform

## ⚙️ Configuration

Key environment variables:

```bash
# Discord
DISCORD_BOT_TOKEN=your_token_here
DISCORD_GUILD_IDS=123456789,987654321

# Google Gemini
GOOGLE_API_KEY=your_key_here

# Printful
PRINTFUL_API_KEY=your_key_here
PRINTFUL_STORE_ID=your_store_id_here

# Optional: Langsmith tracing
LANGCHAIN_API_KEY=your_key_here
LANGCHAIN_TRACING_V2=true

# Bot behavior
BOT_TRIGGER_KEYWORDS=tshirt,t-shirt,shirt,merch
BOT_LOG_LEVEL=INFO
```

## 🚀 Deployment

### Docker

```bash
docker-compose up -d
```

### Google Cloud Run

```bash
./deploy.sh
```

See [Deployment Guide](docs/DEPLOYMENT.md) for detailed instructions.

## 🔒 Security

- API keys stored in environment variables or Google Secret Manager
- No credentials committed to code
- HTTPS for all API communications
- Input validation and sanitization
- Error messages don't leak sensitive information

## 📊 Monitoring

- Structured logging to console and files
- Optional Langsmith integration for LLM tracing
- Google Cloud Logging integration
- Performance metrics and error tracking

## 🛠️ Development

### Running Tests

```bash
# Install dependencies (including dev tools)
uv pip install -r requirements-dev.txt

# Run all tests
pytest

# Run with coverage
pytest --cov=src --cov-report=term

# Run specific test file
pytest tests/test_llm_parser.py -v
```

See **[Testing Guide](docs/TESTING.md)** for comprehensive testing documentation.

### Code Formatting

```bash
# Format code
black src/ tests/

# Lint code
ruff check src/ tests/

# Fix linting issues
ruff check --fix src/ tests/
```

### Continuous Integration

Run code quality checks locally:

```bash
# Format code
black src/ tests/

# Lint code
ruff check src/ tests/

# Run tests
pytest --cov=src
```

For automated deployment, this project uses **Google Cloud Build** (see `cloudbuild.yaml`).

## 🤝 Contributing

Contributions are welcome! Please:

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🎯 Future Enhancements

- [ ] AI-generated graphics using DALL-E or Stable Diffusion
- [ ] Support for multiple product types (hoodies, mugs, stickers)
- [ ] User preference memory
- [ ] Order tracking and webhooks
- [ ] Web dashboard for monitoring
- [ ] Multi-language support
- [ ] Custom font selection
- [ ] Design preview before ordering
- [ ] A/B testing for designs

## 🐛 Troubleshooting

### Bot doesn't respond

- Check Message Content Intent is enabled in Discord Developer Portal
- Verify bot has read/send message permissions
- Check bot token is correct

### LLM errors

- Verify Google API key is valid
- Check API quotas and limits
- Review logs for specific errors

### Printful errors

- Verify API key is correct
- Ensure Printful store is set up
- Check rate limits

See [Setup Guide](docs/SETUP.md) for more troubleshooting tips.

## 📧 Support

For issues and questions:
- Check the [documentation](docs/)
- Review existing issues
- Create a new issue with details

## 🙏 Acknowledgments

- **Discord.py** community for excellent documentation
- **LangChain** for LLM orchestration tools
- **Google Gemini** for powerful language understanding
- **Printful** for print-on-demand API
- All contributors and users!

---

Made with ❤️ and ☕

**Note**: This bot creates products in your Printful account. Make sure you understand Printful's pricing and terms before deploying in production.
