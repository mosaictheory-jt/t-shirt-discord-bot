# Teemill to Prodigi Migration - Instructions

## ✅ Migration Complete

The Discord T-Shirt Bot has been successfully migrated from Teemill to Prodigi Print API.

## 📋 Changes Summary

### Files Added
- `src/services/prodigi_client.py` - New Prodigi API client
- `tests/test_prodigi_client.py` - Test suite for Prodigi client
- `docs/PRODIGI_MIGRATION.md` - Detailed migration documentation
- `PRODIGI_MIGRATION_COMPLETE.md` - Migration summary
- `MIGRATION_INSTRUCTIONS.md` - This file

### Files Deleted
- `src/services/teemill_client.py` - Replaced by prodigi_client.py
- `tests/test_teemill_client.py` - Replaced by test_prodigi_client.py

### Files Modified
- `src/config.py` - Updated to use `prodigi_api_key`
- `src/services/orchestrator.py` - Uses ProdigiClient instead of TeemillClient
- `src/bot/discord_bot.py` - Updated product URLs
- `tests/conftest.py` - Updated environment variables
- `tests/test_config.py` - Updated configuration tests
- `tests/test_orchestrator.py` - Updated to use ProdigiProduct
- `tests/test_design_tracking.py` - Updated for Prodigi API structure
- `tests/integration/test_full_workflow.py` - Updated integration tests
- `README.md` - Updated references to Prodigi
- `docs/SETUP.md` - Updated setup instructions
- `docs/ARCHITECTURE.md` - Updated architecture documentation

## 🚀 Quick Start

### 1. Get Prodigi API Key

1. Visit https://dashboard.prodigi.com/
2. Sign up or log in
3. Navigate to API settings
4. Generate an API key
5. Copy the key

### 2. Update Environment Variables

Update your `.env` file:

```bash
# OLD - Remove this
# TEEMILL_API_KEY=your_teemill_key

# NEW - Add this
PRODIGI_API_KEY=your_prodigi_api_key_here
```

### 3. Test Locally (Optional)

```bash
# Install dependencies
uv pip install -r requirements-dev.txt

# Run tests
pytest tests/test_prodigi_client.py -v
pytest tests/test_orchestrator.py -v

# Run the bot
python -m src.main
```

### 4. Deploy

Update your deployment environment variables:
- Remove: `TEEMILL_API_KEY`
- Add: `PRODIGI_API_KEY`

Then deploy as usual:

```bash
# For Google Cloud Run
./deploy.sh

# For Docker
docker-compose up -d --build
```

## 📖 Documentation

- **Migration Details:** See `docs/PRODIGI_MIGRATION.md`
- **Setup Guide:** See `docs/SETUP.md`
- **Architecture:** See `docs/ARCHITECTURE.md`

## 🔍 What Changed

### API Endpoint
- **Old:** `https://api.teemill.com/v1`
- **New:** `https://api.prodigi.com/v4.0`

### Authentication
- **Old:** `Authorization: Bearer {key}`
- **New:** `X-API-Key: {key}`

### Product URLs
- **Old:** `https://teemill.com/order/{order_id}`
- **New:** `https://dashboard.prodigi.com/orders/{order_id}`

### Default Product
- **SKU:** `GLOBAL-TSHU-CLAS-MENS-MEDI-WHIT`
- **Type:** Classic Unisex T-Shirt
- **Size:** Medium
- **Color:** White

## ✨ Benefits

1. **Global Fulfillment** - Worldwide shipping and production
2. **Better Quality** - Professional-grade products
3. **More Products** - Expandable to hoodies, mugs, etc.
4. **Stable API** - Mature, well-documented v4.0 API
5. **Order Tracking** - Better order management

## 🧪 Testing Checklist

Before going live:
- [ ] Prodigi API key configured
- [ ] Bot connects to Discord
- [ ] Bot can create orders
- [ ] `!mydesigns` command works
- [ ] Product URLs are accessible
- [ ] Logs show successful operations

## ⚠️ Important Notes

1. **No code changes needed** - All migration is complete
2. **Only update API key** - Just change the environment variable
3. **Product URLs changed** - They now point to Prodigi dashboard
4. **Currency changed** - From GBP to USD

## 🆘 Troubleshooting

### "PRODIGI_API_KEY not found"
- Make sure you've updated your `.env` file or deployment environment variables
- The variable name changed from `TEEMILL_API_KEY` to `PRODIGI_API_KEY`

### "Prodigi API error"
- Verify your API key is correct
- Check you have a valid Prodigi account
- Review Prodigi API rate limits

### Tests failing
- Make sure all dependencies are installed: `uv pip install -r requirements-dev.txt`
- Verify environment variables are set

## 📞 Support

- **Prodigi Dashboard:** https://dashboard.prodigi.com/
- **Migration Guide:** `docs/PRODIGI_MIGRATION.md`
- **General Setup:** `docs/SETUP.md`

## 🎉 Ready to Deploy!

The migration is complete. Just update your API key and deploy!

```bash
# Update .env
echo "PRODIGI_API_KEY=your_key_here" >> .env

# Deploy
./deploy.sh
```

---

**Migration Date:** 2025-11-16  
**Status:** ✅ Complete and Ready
