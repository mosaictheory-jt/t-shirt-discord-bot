# Migration from Teemill to Printify API - Summary

**Date:** November 24, 2025  
**Status:** ✅ Complete

Successfully migrated the Discord T-Shirt Bot from Teemill API to Printify API.

---

## Changes Overview

### 1. New Printify Client (`src/services/printify_client.py`)

Created new `PrintifyClient` class to replace `TeemillClient`:

- **API Base URL**: `https://api.printify.com/v1`
- **Authentication**: Bearer token in Authorization header
- **Shop ID**: Required for all product operations
- **Blueprint System**: Uses Printify's blueprint system for product templates
  - Default blueprint: Unisex Heavy Cotton Tee (ID: 5)
  - Configurable print provider (default: 99)

#### Key Methods

- `create_product()` - Creates a new product with design
- `_upload_design_image()` - Uploads image to Printify
- `_get_blueprint()` - Retrieves blueprint details with variants
- `publish_product()` - Publishes product to store
- `get_product_info()` - Gets product details
- `list_products()` - Lists all products with pagination
- `search_products_by_user()` - Finds products by user ID
- `get_all_designs()` - Retrieves all designs
- `get_design_stats()` - Gets design statistics

### 2. Updated Configuration (`src/config.py`)

**Removed:**
- `teemill_api_key`

**Added:**
- `printify_api_key` - Printify API authentication key
- `printify_shop_id` - Printify shop identifier

### 3. Updated Orchestrator (`src/services/orchestrator.py`)

- Replaced `TeemillClient` with `PrintifyClient`
- Updated all references from `teemill_client` to `printify_client`
- Changed product URL generation to use Printify format
- Updated logging messages

### 4. Updated Discord Bot (`src/bot/discord_bot.py`)

- Updated design history display to use Printify product structure
- Changed product URLs from Teemill to Printify format
- Updated field mappings:
  - `name` → `title`
  - `order_id` → `id` (product_id)

### 5. Updated Tests

**New File:**
- `tests/test_printify_client.py` - Complete test suite for Printify client

**Updated Files:**
- `tests/test_orchestrator.py` - Uses `PrintifyProduct` instead of `TeemillProduct`
- `tests/test_design_tracking.py` - Updated to work with Printify API structure
- `tests/integration/test_full_workflow.py` - Uses `PrintifyProduct` mocks
- `tests/test_config.py` - Uses `printify_api_key` and `printify_shop_id`
- `tests/conftest.py` - Uses `PRINTIFY_API_KEY` and `PRINTIFY_SHOP_ID` environment variables

**Deleted Files:**
- `tests/test_teemill_client.py` (replaced by test_printify_client.py)
- `src/services/teemill_client.py` (replaced by printify_client.py)

### 6. Updated Environment Configuration

**File:** `.env.example`

**Before (Teemill):**
```bash
TEEMILL_API_KEY=your_key
```

**After (Printify):**
```bash
PRINTIFY_API_KEY=your_printify_api_key_here
PRINTIFY_SHOP_ID=your_printify_shop_id_here
```

---

## API Comparison

### Teemill → Printify Mapping

| Teemill | Printify | Notes |
|---------|----------|-------|
| Order ID | Product ID | Main identifier |
| Product Code | Blueprint ID | Product template |
| Variant | Variant | Size/color options |
| order_id | id | Field name change |
| name | title | Field name change |
| GBP currency | USD currency | Printify uses USD by default |
| teemill.com/order/{id} | printify.com/app/products/{id} | URL format |

### Product Model Comparison

#### TeemillProduct
```python
order_id: str
product_id: str
variant_id: str
external_id: str
name: str
thumbnail_url: str
retail_price: float
currency: str = "GBP"
product_url: str
```

#### PrintifyProduct
```python
product_id: str
title: str
description: str
blueprint_id: int
print_provider_id: int
variant_id: int
external_id: str
thumbnail_url: str
retail_price: float
currency: str = "USD"
product_url: str
publish_status: str
```

---

## Printify API Integration Details

### Authentication
```python
headers = {
    "Authorization": f"Bearer {api_key}",
    "Content-Type": "application/json"
}
```

### Image Upload
- **Endpoint**: `POST /v1/uploads/images.json`
- **Methods**: URL or base64 content
- **Returns**: Image ID for use in product creation

### Blueprint System
- **Endpoint**: `GET /v1/catalog/blueprints/{blueprint_id}/print_providers/{provider_id}/variants.json`
- **Returns**: Available variants, sizes, colors, and print areas

### Product Creation
- **Endpoint**: `POST /v1/shops/{shop_id}/products.json`
- **Requires**:
  - Blueprint ID
  - Print provider ID
  - Image ID
  - Variants with prices
  - Print areas configuration

### Product Publishing
- **Endpoint**: `POST /v1/shops/{shop_id}/products/{product_id}/publish.json`
- **Purpose**: Makes product available in connected stores

---

## Configuration Steps

### 1. Obtain Printify Credentials

1. Create a Printify account at https://printify.com
2. Set up a shop
3. Generate an API key from the API settings
4. Note your shop ID

### 2. Update Environment Variables

```bash
# Set in your .env file or deployment environment
PRINTIFY_API_KEY=your_actual_api_key_here
PRINTIFY_SHOP_ID=your_actual_shop_id_here
```

### 3. Configure Blueprint and Print Provider (Optional)

In `src/services/printify_client.py`, you can adjust:

```python
# Default blueprint (product type)
BLUEPRINT_UNISEX_TSHIRT = 5  # Unisex Heavy Cotton Tee

# Default print provider (varies by region)
DEFAULT_PRINT_PROVIDER_ID = 99
```

Refer to Printify's catalog API to find other blueprints and providers.

---

## Breaking Changes

### For Developers

1. **API Client Change**: All code using `TeemillClient` must update to `PrintifyClient`
2. **Product Model**: Update code using `TeemillProduct` to `PrintifyProduct`
3. **Field Names**: 
   - `order_id` → `product_id`
   - `name` → `title`
4. **Currency**: Default changed from GBP to USD
5. **URL Format**: Product URLs now point to Printify app instead of Teemill orders

### For Deployment

1. Update all environment variables in your deployment platform
2. Set `PRINTIFY_API_KEY` and `PRINTIFY_SHOP_ID`
3. Remove `TEEMILL_API_KEY` from environment

---

## Testing

All tests have been updated to work with the Printify API:

```bash
# Run all tests
pytest tests/ -v

# Run specific test suites
pytest tests/test_printify_client.py -v
pytest tests/test_orchestrator.py -v
pytest tests/integration/test_full_workflow.py -v
```

---

## Documentation References

### Printify API Documentation
- **Main Docs**: https://developers.printify.com/
- **Create Product**: https://developers.printify.com/#create-a-new-product
- **Upload Image**: https://developers.printify.com/#upload-an-image
- **Blueprints**: https://developers.printify.com/#blueprints
- **Publish Product**: https://developers.printify.com/#publish-a-product

### Internal Documentation
- Update README.md with Printify setup instructions
- Update API_REFERENCE.md with Printify client documentation
- Update DEPLOYMENT.md with new environment variables

---

## Next Steps

1. ✅ Core API integration complete
2. ✅ All tests updated
3. ✅ Configuration migrated
4. ⏳ Update external documentation (README, API_REFERENCE)
5. ⏳ Deploy to staging environment for testing
6. ⏳ Verify integration with real Printify API
7. ⏳ Test product creation end-to-end
8. ⏳ Deploy to production

---

## Rollback Plan

If issues arise, the previous Teemill implementation can be restored from git history:

```bash
git checkout <commit-before-migration>
```

Or selectively restore files:
```bash
git checkout <commit> -- src/services/teemill_client.py
git checkout <commit> -- tests/test_teemill_client.py
```

---

## Files Modified

### Source Code
- ✅ `src/services/printify_client.py` (NEW)
- ✅ `src/services/orchestrator.py` (UPDATED)
- ✅ `src/config.py` (UPDATED)
- ✅ `src/bot/discord_bot.py` (UPDATED)
- ❌ `src/services/teemill_client.py` (DELETED)

### Tests
- ✅ `tests/test_printify_client.py` (NEW)
- ✅ `tests/test_orchestrator.py` (UPDATED)
- ✅ `tests/test_design_tracking.py` (UPDATED)
- ✅ `tests/test_config.py` (UPDATED)
- ✅ `tests/conftest.py` (UPDATED)
- ✅ `tests/integration/test_full_workflow.py` (UPDATED)
- ❌ `tests/test_teemill_client.py` (DELETED)

### Configuration
- ✅ `.env.example` (UPDATED)

### Documentation
- ✅ `docs/PRINTIFY_MIGRATION_SUMMARY.md` (NEW - this file)

---

## Summary

The migration from Teemill to Printify API is complete. All source code, tests, and configuration have been updated. The system now uses Printify's more robust product creation API with support for blueprints, multiple print providers, and better product management.

**Key Benefits of Printify:**
- More print providers and locations
- Better product catalog
- More customization options
- Robust publishing system
- Better API documentation
- More competitive pricing

**Migration Status:** ✅ Complete and ready for testing
