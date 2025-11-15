# Design Tracking and History

This guide explains how the bot tracks all past designs and how to access design history.

## Overview

All designs created by the bot are automatically tracked in your Printful store. Each design is stored as a "sync product" with metadata that allows you to:

- View all designs ever created
- Filter designs by user
- Track design statistics
- Access design history from Discord

## How Tracking Works

### Automatic Storage

Every time a user requests a t-shirt:

1. **Design Created**: Bot generates the design image
2. **Uploaded to Printful**: Design is uploaded to your Printful store
3. **Sync Product Created**: A sync product is created with:
   - Product name (includes the phrase)
   - Thumbnail image
   - External ID (tracks the Discord user)
   - Timestamp (creation date)

### External ID Format

Each product gets a unique external ID in the format:
```
discord_{user_id}_{hash}
```

Example: `discord_123456789_-8675309`

This allows filtering designs by user while ensuring uniqueness.

## Accessing Design History

### 1. Discord Commands

#### View Your Own Designs

Users can see their design history by typing:
```
!mydesigns
```

**Response Example**:
```
Your Design History (3 designs):

1. Hello World - Custom Tee
   🔗 View: https://www.printful.com/dashboard/store/products/12345

2. Code is Life - Custom Tee
   🔗 View: https://www.printful.com/dashboard/store/products/12346

3. Coffee First - Custom Tee
   🔗 View: https://www.printful.com/dashboard/store/products/12347
```

### 2. Printful Dashboard

#### View All Designs

1. Log in to [Printful Dashboard](https://www.printful.com/dashboard)
2. Go to **Stores** → Select your store
3. Click **Products** in the left sidebar
4. See all created designs with:
   - Thumbnail preview
   - Product name
   - Creation date
   - Sales statistics

#### Search and Filter

In the Printful dashboard, you can:
- **Search** by product name
- **Sort** by date created, name, or sales
- **Filter** by product type
- **View details** for each design

### 3. Programmatic Access

#### Get User's Designs

```python
from src.services.orchestrator import TShirtOrchestrator

orchestrator = TShirtOrchestrator()
await orchestrator.initialize()

# Get designs for specific user
user_id = "123456789"
designs = await orchestrator.get_user_designs(user_id)

for design in designs:
    print(f"Design: {design['name']}")
    print(f"Created: {design['created']}")
    print(f"ID: {design['id']}")
```

#### Get All Designs

```python
# Get all designs in store
all_designs = await orchestrator.get_all_designs()
print(f"Total designs: {len(all_designs)}")
```

#### Get Statistics

```python
# Get design statistics
stats = await orchestrator.get_design_statistics()
print(f"Total designs: {stats['total_designs']}")
print(f"Unique users: {stats['unique_users']}")
print(f"Designs per user: {stats['designs_per_user']:.1f}")
```

## Design Data Structure

Each design in the store contains:

```python
{
    "id": 12345,                          # Sync product ID
    "external_id": "discord_123_-456",   # User tracking
    "name": "Hello World - Custom Tee",  # Product name
    "thumbnail_url": "https://...",       # Design preview
    "created": 1234567890,               # Unix timestamp
    "variants": [...],                   # Product variants
    "synced": 1                          # Sync status
}
```

## Use Cases

### 1. User Design History

**Scenario**: User wants to see what designs they've created

**Solution**: Use `!mydesigns` command in Discord

**Benefits**:
- Quick access to past designs
- Easy reordering
- Track personal design portfolio

### 2. Popular Designs

**Scenario**: Find which designs are most popular

**Method**:
```python
# Get all designs
designs = await orchestrator.get_all_designs()

# Check Printful dashboard for sales data
# Designs with sales will show in the statistics
```

### 3. Design Analytics

**Scenario**: Understand bot usage and patterns

**Method**:
```python
stats = await orchestrator.get_design_statistics()
print(f"Total designs: {stats['total_designs']}")
print(f"Active users: {stats['unique_users']}")
print(f"Avg designs/user: {stats['designs_per_user']:.1f}")
```

### 4. Design Backup

**Scenario**: Export all designs for backup

**Method**:
```python
import json

# Get all designs
designs = await orchestrator.get_all_designs()

# Save to file
with open('designs_backup.json', 'w') as f:
    json.dump(designs, f, indent=2)
```

## Storage Limits

### Printful Store Limits

- **Products**: No hard limit on Printful
- **Storage**: Unlimited design storage
- **API Rate**: 120 requests/minute

### Best Practices

1. **Regular Backups**: Export design data periodically
2. **Monitor Storage**: Check Printful dashboard regularly
3. **Clean Old Designs**: Archive or remove unused designs
4. **Organize Names**: Use consistent naming conventions

## Design Privacy

### User Privacy

- External IDs contain Discord user IDs
- User IDs are hashed for privacy
- Only bot owner can see all designs
- Users can only see their own designs via `!mydesigns`

### Access Control

- **Users**: Can view their own designs
- **Bot Owner**: Can view all designs via Printful dashboard
- **Admin Commands**: Could be added for moderation

## Troubleshooting

### Designs Not Showing

**Problem**: `!mydesigns` returns no results

**Solutions**:
1. Check user has created designs
2. Verify Printful API key is correct
3. Check external ID format in Printful
4. Review bot logs for errors

### Missing Design Data

**Problem**: Design information incomplete

**Solutions**:
1. Check Printful dashboard directly
2. Verify sync product was created
3. Check API rate limits
4. Review error logs

### Performance Issues

**Problem**: Slow design history retrieval

**Solutions**:
1. Implement caching for design lists
2. Use pagination for large stores
3. Limit results in `!mydesigns` command
4. Consider database cache layer

## Future Enhancements

Potential improvements for design tracking:

### Database Integration

Add a database to cache design information:

```python
# Cache design metadata
designs_db = {
    "user_id": "123456789",
    "design_id": 12345,
    "phrase": "Hello World",
    "created_at": "2024-01-15T10:30:00Z",
    "printful_url": "https://...",
}
```

**Benefits**:
- Faster lookups
- More filtering options
- Better analytics
- Reduced API calls

### Admin Dashboard

Web interface to view:
- All designs
- User statistics
- Popular phrases
- Revenue tracking

### Design Collections

Group designs by:
- User
- Date range
- Theme
- Popularity

### Sharing Features

Allow users to:
- Share designs with friends
- Create collections
- Vote on favorite designs
- Request similar designs

## API Reference

### Printful Client Methods

#### `search_products_by_user(user_id: str) -> list`

Get all products for a specific user.

**Parameters**:
- `user_id` (str): Discord user ID

**Returns**:
- List of product dictionaries

**Example**:
```python
designs = await printful_client.search_products_by_user("123456789")
```

#### `get_all_designs() -> list`

Get all products in the store.

**Returns**:
- List of all product dictionaries

**Example**:
```python
all_designs = await printful_client.get_all_designs()
```

#### `get_design_stats() -> dict`

Get statistics about designs.

**Returns**:
- Dictionary with stats: `total_designs`, `unique_users`, `designs_per_user`, `latest_design`

**Example**:
```python
stats = await printful_client.get_design_stats()
print(f"Total: {stats['total_designs']}")
```

### Orchestrator Methods

#### `get_user_designs(user_id: str) -> list`

Get designs for a user (wrapper around Printful client).

**Parameters**:
- `user_id` (str): Discord user ID

**Returns**:
- List of design dictionaries

#### `get_design_statistics() -> dict`

Get design statistics (wrapper around Printful client).

**Returns**:
- Dictionary with statistics

#### `get_all_designs() -> list`

Get all designs (wrapper around Printful client).

**Returns**:
- List of all designs

## Additional Resources

- [Printful API Documentation](https://developers.printful.com/docs/)
- [Printful Store Management](https://www.printful.com/dashboard/store)
- [Discord Bot Commands](SETUP.md#bot-commands)

## Questions?

- Check [Troubleshooting](#troubleshooting)
- Review [API Reference](#api-reference)
- Open an issue with the `design-tracking` label
