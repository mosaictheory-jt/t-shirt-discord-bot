# API Reference

## Core Services

### LLMParser

Parses user messages to extract t-shirt design details using Google Gemini.

#### `parse_message(message: str) -> Optional[TShirtRequest]`

Parses a user message and extracts structured t-shirt request information.

**Parameters:**
- `message` (str): The user's message requesting a t-shirt

**Returns:**
- `TShirtRequest` or `None`: Structured request details or None if parsing fails

**Example:**
```python
parser = LLMParser()
request = await parser.parse_message("I want a retro shirt that says 'Code is Life'")

print(request.phrase)  # "Code is Life"
print(request.style)   # "retro"
```

### TShirtRequest Model

Structured output from the LLM parser.

**Fields:**
- `phrase` (str): The main text to put on the t-shirt
- `style` (str): Text style (bold, script, modern, retro, graffiti, etc.)
- `wants_image` (bool): Whether the user wants an accompanying image
- `image_description` (Optional[str]): Description of requested image
- `color_preference` (Optional[str]): Preferred colors, if mentioned

**Example:**
```python
from src.services.llm_parser import TShirtRequest

request = TShirtRequest(
    phrase="Hello World",
    style="modern",
    wants_image=False,
    image_description=None,
    color_preference="blue"
)
```

---

### DesignGenerator

Generates t-shirt design images using PIL/Pillow.

#### `generate_design(request: TShirtRequest) -> Tuple[Path, bytes]`

Creates a high-resolution t-shirt design image.

**Parameters:**
- `request` (TShirtRequest): The parsed t-shirt request

**Returns:**
- `Tuple[Path, bytes]`: File path to saved image and image bytes

**Image Specifications:**
- Format: PNG with transparency (RGBA)
- Dimensions: 4500x5400 pixels (Printful standard)
- DPI: 300 (print quality)

**Example:**
```python
generator = DesignGenerator()
file_path, image_bytes = await generator.generate_design(request)

print(f"Design saved to: {file_path}")
print(f"Image size: {len(image_bytes)} bytes")
```

#### Design Features

- **Automatic Font Sizing**: Scales based on text length
- **Text Outlining**: Adds outline for visibility on any background
- **Style Effects**: Applies style-specific visual effects
- **Color Customization**: Respects user color preferences
- **Centered Layout**: Professional centered text placement

---

### PrintfulClient

Client for interacting with the Printful API.

#### `initialize() -> None`

Initializes the HTTP session. Must be called before making API requests.

**Example:**
```python
client = PrintfulClient()
await client.initialize()
```

#### `cleanup() -> None`

Closes the HTTP session. Should be called before shutdown.

**Example:**
```python
await client.cleanup()
```

#### `create_product(design_image_url: str, product_name: str, user_id: str) -> PrintfulProduct`

Creates a new product on Printful with the design.

**Parameters:**
- `design_image_url` (str): URL or base64-encoded image data
- `product_name` (str): Name for the product
- `user_id` (str): User ID for tracking

**Returns:**
- `PrintfulProduct`: Product details including ID and URL

**Example:**
```python
product = await client.create_product(
    design_image_url="data:image/png;base64,iVBORw0KGgoAAAA...",
    product_name="Hello World - Custom Tee",
    user_id="discord_12345"
)

print(f"Product ID: {product.sync_product_id}")
print(f"Price: ${product.retail_price}")
```

#### `get_product_info(sync_product_id: int) -> Dict`

Retrieves product information from Printful.

**Parameters:**
- `sync_product_id` (int): The sync product ID from Printful

**Returns:**
- `Dict`: Product information

**Example:**
```python
info = await client.get_product_info(12345)
print(info['sync_product']['name'])
```

#### `list_products() -> List[Dict]`

Lists all products in the Printful store.

**Returns:**
- `List[Dict]`: List of product dictionaries

**Example:**
```python
products = await client.list_products()
for product in products:
    print(f"- {product['name']}")
```

### PrintfulProduct Model

Product information returned from Printful.

**Fields:**
- `product_id` (int): Printful product template ID
- `variant_id` (int): Printful variant ID
- `sync_product_id` (Optional[int]): Sync product ID in Printful store
- `external_id` (Optional[str]): External reference ID
- `name` (str): Product name
- `thumbnail_url` (Optional[str]): URL to product thumbnail
- `retail_price` (Optional[float]): Retail price
- `currency` (str): Currency code (default: "USD")

---

### TShirtOrchestrator

Main orchestrator that coordinates the entire workflow.

#### `initialize() -> None`

Initializes all services.

**Example:**
```python
orchestrator = TShirtOrchestrator()
await orchestrator.initialize()
```

#### `cleanup() -> None`

Cleans up all services.

**Example:**
```python
await orchestrator.cleanup()
```

#### `process_tshirt_request(message: str, user_id: str, username: str) -> TShirtResult`

Processes a complete t-shirt request end-to-end.

**Parameters:**
- `message` (str): The user's message
- `user_id` (str): Discord user ID
- `username` (str): Discord username

**Returns:**
- `TShirtResult`: Result with success status and product URL

**Workflow:**
1. Parse message with LLM
2. Generate design image
3. Upload to Printful
4. Create product
5. Return result

**Example:**
```python
result = await orchestrator.process_tshirt_request(
    message="I want a shirt that says 'Python Rocks'",
    user_id="123456789",
    username="CoolUser#1234"
)

if result.success:
    print(f"Success! Product URL: {result.product_url}")
    print(f"Response: {result.response_phrase}")
else:
    print(f"Error: {result.error_message}")
```

### TShirtResult Model

Result of a t-shirt creation request.

**Fields:**
- `success` (bool): Whether the request succeeded
- `product_url` (Optional[str]): URL to the created product
- `response_phrase` (str): Fun phrase to send to user
- `error_message` (Optional[str]): Error message if failed
- `phrase` (Optional[str]): The phrase that was put on the shirt

---

### TShirtBot

Main Discord bot class.

#### Initialization

```python
bot = TShirtBot()
```

The bot automatically:
- Sets up Discord intents
- Initializes the orchestrator
- Configures event handlers

#### `start(token: str) -> None`

Starts the bot with the provided token.

**Parameters:**
- `token` (str): Discord bot token

**Example:**
```python
await bot.start(settings.discord_bot_token)
```

#### `close() -> None`

Closes the bot and cleans up resources.

**Example:**
```python
await bot.close()
```

#### Event Handlers

##### `on_ready()`

Called when the bot successfully connects to Discord.

##### `on_message(message: discord.Message)`

Called for every message the bot can see. Automatically:
- Ignores bot messages
- Checks for trigger keywords
- Processes t-shirt requests
- Replies to users

---

## Configuration

### Settings Class

All configuration is managed through the `Settings` class in `src/config.py`.

#### Environment Variables

**Discord:**
- `DISCORD_BOT_TOKEN`: Discord bot token (required)
- `DISCORD_GUILD_IDS`: Comma-separated guild IDs (optional)

**Google:**
- `GOOGLE_API_KEY`: Google API key for Gemini (required)

**Langsmith:**
- `LANGCHAIN_API_KEY`: Langsmith API key (optional)
- `LANGCHAIN_TRACING_V2`: Enable tracing (default: true)
- `LANGCHAIN_PROJECT`: Project name (default: "discord-tshirt-bot")

**Printful:**
- `PRINTFUL_API_KEY`: Printful API key (required)

**Bot:**
- `BOT_TRIGGER_KEYWORDS`: Keywords that trigger the bot (default: "tshirt,t-shirt,shirt,merch")
- `BOT_LOG_LEVEL`: Logging level (default: "INFO")

#### Properties

##### `trigger_keywords_list: List[str]`

Returns trigger keywords as a list.

##### `guild_ids_list: List[int]`

Returns guild IDs as a list of integers.

#### Methods

##### `setup_logging() -> None`

Configures the logging system.

**Example:**
```python
from src.config import settings

settings.setup_logging()
```

---

## Error Handling

All services implement comprehensive error handling:

### LLMParser
- Falls back to simple parsing if Gemini fails
- Logs all parsing errors
- Never returns None (uses fallback)

### DesignGenerator
- Validates input parameters
- Falls back to default fonts if custom fonts unavailable
- Raises exceptions for critical errors

### PrintfulClient
- Handles HTTP errors gracefully
- Retries on transient failures
- Logs all API errors with details

### TShirtOrchestrator
- Catches all exceptions
- Returns structured error results
- Provides user-friendly error messages
- Logs detailed error information

---

## Logging

All components use Python's `logging` module:

```python
import logging

logger = logging.getLogger(__name__)

logger.info("Processing request...")
logger.warning("Rate limit approaching")
logger.error("API call failed", exc_info=True)
```

**Log Levels:**
- `DEBUG`: Detailed debugging information
- `INFO`: General information about operations
- `WARNING`: Warning messages
- `ERROR`: Error messages with stack traces

**Configuration:**
```python
from src.config import settings

settings.BOT_LOG_LEVEL = "DEBUG"
settings.setup_logging()
```

---

## Testing

### Unit Tests

```python
import pytest
from src.services.llm_parser import LLMParser

@pytest.mark.asyncio
async def test_parse_message():
    parser = LLMParser()
    request = await parser.parse_message("I want a shirt that says 'Test'")
    
    assert request is not None
    assert "Test" in request.phrase
```

### Integration Tests

```python
@pytest.mark.asyncio
async def test_full_workflow():
    orchestrator = TShirtOrchestrator()
    await orchestrator.initialize()
    
    result = await orchestrator.process_tshirt_request(
        message="Make me a shirt",
        user_id="test_user",
        username="TestUser"
    )
    
    assert result.success
    assert result.product_url is not None
    
    await orchestrator.cleanup()
```

---

## Rate Limits

### Printful API
- 120 requests per minute
- Enforced by Printful
- Client automatically handles rate limit responses

### Google Gemini API
- Varies by plan
- Typically 60 requests per minute for free tier
- Check your quota at Google AI Studio

### Discord API
- Message send: 5 per 5 seconds per channel
- Bot automatically handles rate limiting

---

## Best Practices

1. **Always initialize services:**
   ```python
   await client.initialize()
   try:
       # Use client
   finally:
       await client.cleanup()
   ```

2. **Use context managers when possible:**
   ```python
   async with aiohttp.ClientSession() as session:
       # Use session
   ```

3. **Handle errors gracefully:**
   ```python
   try:
       result = await process_request()
   except Exception as e:
       logger.error(f"Error: {e}", exc_info=True)
       return error_result
   ```

4. **Log important events:**
   ```python
   logger.info(f"Processing request for user {user_id}")
   ```

5. **Validate inputs:**
   ```python
   if not message or len(message) > 500:
       raise ValueError("Invalid message length")
   ```
