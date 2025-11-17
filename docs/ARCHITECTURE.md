# Architecture Documentation

## Overview

The Discord T-Shirt Bot is a Python-based application that automatically creates custom t-shirts based on user messages in Discord channels. It uses several integrated services to accomplish this:

1. **Discord Bot** - Monitors messages and responds to users
2. **Gemini LLM** - Parses user messages to extract design details
3. **Design Generator** - Creates t-shirt design images
4. **Prodigi Print API** - Handles product creation and fulfillment

## System Architecture

```
┌─────────────────┐
│  Discord User   │
└────────┬────────┘
         │ Message: "I want a t-shirt that says 'Hello World'"
         ▼
┌─────────────────────────────────────────────────────────┐
│                    Discord Bot                           │
│  - Monitors all messages                                 │
│  - Detects trigger keywords                              │
│  - Manages responses                                     │
└────────┬────────────────────────────────────────────────┘
         │
         ▼
┌─────────────────────────────────────────────────────────┐
│                  Orchestrator                            │
│  - Coordinates workflow                                  │
│  - Error handling                                        │
│  - Response generation                                   │
└────┬────────┬────────┬──────────────────────────────────┘
     │        │        │
     ▼        ▼        ▼
┌─────────┐ ┌─────────┐ ┌──────────────┐
│   LLM   │ │ Design  │ │   Prodigi    │
│ Parser  │ │Generator│ │    Client    │
└─────────┘ └─────────┘ └──────────────┘
     │            │             │
     ▼            ▼             ▼
┌─────────┐ ┌─────────┐ ┌──────────────┐
│ Gemini  │ │  PIL/   │ │   Prodigi    │
│   API   │ │ Pillow  │ │     API      │
└─────────┘ └─────────┘ └──────────────┘
                               │
                               ▼
                        ┌──────────────┐
                        │  T-Shirt     │
                        │  Product     │
                        └──────────────┘
```

## Component Details

### 1. Discord Bot (`src/bot/discord_bot.py`)

**Responsibilities:**
- Connect to Discord using the provided bot token
- Monitor messages in all accessible channels
- Detect messages containing trigger keywords
- Forward requests to the orchestrator
- Reply to users with product links

**Key Features:**
- Asynchronous message handling
- Typing indicators during processing
- Error handling and user feedback
- Logging of all requests

**Technology:**
- `discord.py` - Discord API wrapper
- Async/await for non-blocking I/O

### 2. LLM Parser (`src/services/llm_parser.py`)

**Responsibilities:**
- Parse user messages using Gemini LLM
- Extract design details (phrase, style, colors)
- Determine if images are requested
- Provide structured output

**Input:**
```
"I want a cool retro t-shirt that says 'Born to Code'"
```

**Output:**
```python
TShirtRequest(
    phrase="Born to Code",
    style="retro",
    wants_image=False,
    image_description=None,
    color_preference=None
)
```

**Technology:**
- `langchain` - LLM orchestration framework
- `langchain-google-genai` - Gemini integration
- `pydantic` - Data validation and parsing
- Gemini 2.5 Flash model for fast, accurate parsing

**Features:**
- Structured output using Pydantic models
- Fallback parser for when LLM fails
- Context-aware interpretation
- Handles various message formats

### 3. Design Generator (`src/services/design_generator.py`)

**Responsibilities:**
- Generate high-resolution t-shirt designs
- Render text with various styles
- Apply effects (retro, modern, graffiti)
- Handle color preferences
- Create print-ready images

**Output Specifications:**
- Format: PNG with transparency
- Dimensions: 4500x5400 pixels (Printful standard)
- Color depth: RGBA
- Font: Scalable based on text length

**Technology:**
- `Pillow (PIL)` - Image processing
- Dynamic font sizing
- Text outlining for visibility
- Style effects

**Design Features:**
- Centered text layout
- Automatic font sizing
- Outline/shadow for readability
- Color customization
- Style-specific effects

### 4. Prodigi Client (`src/services/prodigi_client.py`)

**Responsibilities:**
- Upload design images to Prodigi
- Create print-on-demand orders
- Configure products (sizes, colors, SKUs)
- Generate order URLs
- Handle API errors

**Workflow:**
1. Prepare design image (URL or base64)
2. Create an order with the design via Prodigi API
3. Configure product (t-shirt type, size, shipping)
4. Return order URL for tracking

**Technology:**
- `aiohttp` - Async HTTP client
- Prodigi Print API v4.0
- Base64 encoding for image upload
- X-API-Key authentication

**Product Details:**
- Default Product: Classic Unisex T-Shirt (SKU: GLOBAL-TSHU-CLAS-MENS-MEDI-WHIT)
- Default Size: Medium
- Default Color: White
- Shipping: Budget (default)
- Currency: USD

### 5. Orchestrator (`src/services/orchestrator.py`)

**Responsibilities:**
- Coordinate the entire workflow
- Manage service lifecycle
- Handle errors gracefully
- Generate fun response phrases
- Log all operations

**Workflow:**
1. Receive message from Discord bot
2. Parse message with LLM
3. Generate design image
4. Upload to Prodigi and create order
5. Return order URL to Discord bot

**Features:**
- Async/await for concurrent operations
- Comprehensive error handling
- Langsmith tracing (optional)
- Random response phrases for personality

## Data Flow

### Successful Request Flow

1. User posts: "Make me a shirt that says 'Coffee First'"
2. Discord bot detects trigger keyword "shirt"
3. Bot passes message to orchestrator
4. Orchestrator invokes LLM parser
5. Gemini extracts: phrase="Coffee First", style="modern"
6. Design generator creates PNG image with text
7. Image uploaded to Prodigi as base64
8. Prodigi creates print-on-demand order
9. Order URL returned to orchestrator
10. Orchestrator selects fun response phrase
11. Bot replies: "Got you fam! 🔥 Check out your custom tee: [URL]"

### Error Handling Flow

If any step fails:
1. Exception caught by orchestrator
2. Error logged with details
3. User-friendly error message sent to Discord
4. No partial products created

## Configuration

### Environment Variables

All configuration is managed through environment variables (see `src/config.py`):

- **Discord**: Bot token, guild IDs
- **Google**: API key for Gemini
- **Prodigi**: API key
- **Langsmith**: API key, project name (optional)
- **Bot**: Trigger keywords, log level

### Settings Management

- Uses `pydantic-settings` for validation
- Type-safe configuration
- Automatic .env file loading
- Validation on startup

## Deployment Architecture

### Docker Container

```
┌─────────────────────────────────────┐
│        Docker Container              │
│  ┌────────────────────────────────┐ │
│  │    Discord Bot Process         │ │
│  │  - Long-running                │ │
│  │  - Event-driven                │ │
│  └────────────────────────────────┘ │
│                                      │
│  ┌────────────────────────────────┐ │
│  │    Generated Images            │ │
│  │  - Temporary storage           │ │
│  │  - Volume mounted              │ │
│  └────────────────────────────────┘ │
│                                      │
│  ┌────────────────────────────────┐ │
│  │    Logs                        │ │
│  │  - Application logs            │ │
│  │  - Volume mounted              │ │
│  └────────────────────────────────┘ │
└─────────────────────────────────────┘
```

### Google Cloud Run

```
┌──────────────────────────────────────┐
│         Cloud Run Service             │
│  - Auto-scaling                       │
│  - Managed container                  │
│  - Integrated logging                 │
│                                       │
│  ┌─────────────────────────────────┐ │
│  │   Discord Bot Container         │ │
│  └─────────────────────────────────┘ │
│         ▲                 │           │
└─────────┼─────────────────┼───────────┘
          │                 │
    ┌─────┴─────┐    ┌──────▼──────┐
    │  Secret   │    │  Cloud      │
    │  Manager  │    │  Logging    │
    └───────────┘    └─────────────┘
```

## Security Considerations

1. **API Keys**: Stored in environment variables or Secret Manager
2. **No Credentials in Code**: All sensitive data externalized
3. **HTTPS**: All API communications over TLS
4. **Input Validation**: User messages sanitized before processing
5. **Rate Limiting**: Printful API has rate limits (handled by client)
6. **Error Messages**: Generic messages to users, detailed logs for admins

## Scalability

### Current Limitations
- Single bot instance
- Sequential request processing
- Local image storage

### Scaling Options
1. **Horizontal Scaling**: Multiple bot instances with sharding
2. **Queue System**: Redis/RabbitMQ for request queue
3. **Cloud Storage**: GCS for generated images
4. **Caching**: Cache LLM responses for similar requests
5. **Load Balancing**: Multiple instances behind load balancer

## Performance Characteristics

### Typical Request Timeline
- Message detection: < 100ms
- LLM parsing: 1-3 seconds
- Image generation: 1-2 seconds
- Prodigi upload/creation: 3-5 seconds
- **Total**: ~5-10 seconds per request

### Resource Usage
- Memory: ~200-500 MB
- CPU: Low (mostly I/O bound)
- Network: ~5-10 MB per request (image upload)
- Storage: ~5 MB per design (temporary)

## Monitoring and Observability

### Logging
- Structured logging with Python logging module
- Log levels: DEBUG, INFO, WARNING, ERROR
- Log destinations: Console, file, Cloud Logging

### Tracing (with Langsmith)
- LLM request tracing
- Performance monitoring
- Error tracking
- Request replay for debugging

### Metrics to Monitor
- Messages processed per minute
- Success/failure rate
- LLM parsing accuracy
- Average response time
- Prodigi API errors
- Bot uptime

## Future Enhancements

1. **AI Image Generation**: Add DALL-E or Stable Diffusion for graphics
2. **Multiple Products**: Support hoodies, mugs, stickers
3. **User Preferences**: Remember user style preferences
4. **Order Tracking**: Track fulfillment status
5. **Admin Dashboard**: Web interface for monitoring
6. **A/B Testing**: Test different design styles
7. **Multi-language**: Support multiple languages
8. **Custom Fonts**: Allow users to specify fonts
9. **Design Preview**: Show design before ordering
10. **Webhook Integration**: Prodigi webhooks for order updates
