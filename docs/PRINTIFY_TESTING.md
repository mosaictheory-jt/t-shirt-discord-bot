# Printify API Integration Testing Guide

## Overview

This document describes how to test the Printify API integration in this project.

## Prerequisites

1. **Printify Account**: Create an account at [printify.com](https://printify.com)
2. **API Key**: Generate an API key from your Printify dashboard under Settings > API Access
3. **Shop ID**: Get your shop ID from the Printify dashboard URL or API

## Setting Up Environment Variables

### Option 1: Using a `.env` file (recommended for local development)

Create a `.env` file in the workspace root:

```bash
# Copy from example
cp .env.example .env

# Edit with your actual values
PRINTIFY_API_KEY=your_actual_api_key_here
PRINTIFY_SHOP_ID=your_actual_shop_id_here
```

### Option 2: Export Environment Variables

```bash
export PRINTIFY_API_KEY=your_actual_api_key_here
export PRINTIFY_SHOP_ID=your_actual_shop_id_here
```

### Option 3: Google Cloud Secret Manager (Production)

Secrets are configured in `cloudbuild.yaml` to be loaded from Google Cloud Secret Manager:
- `printify-api-key`
- `printify-shop-id`

## Running Tests

### Quick API Test (Command Line)

```bash
python scripts/quick_test_printify.py <API_KEY> <SHOP_ID>
```

This will test:
1. API connectivity
2. Shop access
3. Blueprint catalog access
4. Print providers
5. Product listing

### Full Integration Tests

```bash
# With environment variables set
pytest tests/integration/test_printify_integration.py -v

# Or run the manual test script
python tests/integration/test_printify_integration.py
```

### Unit Tests (Mocked)

Unit tests use mocked API responses and don't require real credentials:

```bash
pytest tests/test_printify_client.py -v
```

## API Endpoints Tested

| Endpoint | Purpose | Test Coverage |
|----------|---------|---------------|
| `GET /shops.json` | List all shops | ✓ |
| `GET /shops/{id}.json` | Get shop details | ✓ |
| `GET /catalog/blueprints.json` | List products | ✓ |
| `GET /catalog/blueprints/{id}.json` | Get product details | ✓ |
| `GET /catalog/blueprints/{id}/print_providers.json` | Get providers | ✓ |
| `GET /catalog/blueprints/{id}/print_providers/{id}/variants.json` | Get variants | ✓ |
| `GET /shops/{id}/products.json` | List shop products | ✓ |
| `POST /uploads/images.json` | Upload design image | ✓ |
| `POST /shops/{id}/products.json` | Create product | ✓ |
| `POST /shops/{id}/products/{id}/publish.json` | Publish product | ✓ |

## Common Issues

### 401 Unauthorized
- Check that your API key is correct
- Ensure the key hasn't been revoked
- Verify you're using Bearer token authentication

### 403 Forbidden
- Verify you have access to the shop ID
- Check API key permissions

### 404 Not Found
- Verify the shop ID exists
- Check that the blueprint/product ID is valid

### 429 Rate Limited
- Implement exponential backoff
- Reduce request frequency

## Testing Product Creation

To test the full product creation workflow:

1. **Upload Image**: The system uploads your design image to Printify
2. **Get Variants**: Retrieves available sizes/colors for the product
3. **Create Product**: Creates the product with your design
4. **Publish** (optional): Makes the product available in your store

### Test with Sample Data

```python
import asyncio
from src.services.printify_client import PrintifyClient

async def test_create():
    client = PrintifyClient()
    await client.initialize()
    
    # List products first
    products = await client.list_products(limit=5)
    print(f"Current products: {len(products['products'])}")
    
    # Get design stats
    stats = await client.get_design_stats()
    print(f"Design stats: {stats}")
    
    await client.cleanup()

asyncio.run(test_create())
```

## Cleanup Test Data

Always delete test products after integration tests:

```python
await client.delete_product(product_id)
```

## Security Notes

- Never commit real API keys to version control
- Use environment variables or secret managers
- Log only partial API keys (first 10 + last 4 characters)
- Rotate API keys periodically
