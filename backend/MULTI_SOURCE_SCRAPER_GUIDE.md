# Multi-Source Property Scraper - Complete Guide

## 🎯 Overview

The scraper now supports **4 reliable UK property data sources**:

1. **Land Registry** - Official UK Government data (most reliable for historical sales)
2. **Zoopla** - Major UK property portal
3. **OnTheMarket** - Property portal owned by estate agents
4. **Rightmove** - Largest UK property portal (has bot protection)

## 🚀 Features

✅ Multi-source aggregation for maximum data reliability  
✅ Parallel scraping for speed  
✅ Priority-based fallback strategy  
✅ Cross-validation of data across sources  
✅ Individual source endpoints for targeted queries  
✅ Batch processing support  

## 📡 API Endpoints

### 1. Multi-Source Property Search (Recommended)

**POST /api/property**

Searches across all sources and aggregates results.

```bash
curl -X POST http://localhost:5001/api/property \
  -H "Content-Type: application/json" \
  -d '{
    "address": "Baker Street, London",
    "postcode": "NW1 6XE",
    "strategy": "priority"
  }'
```

**Parameters:**
- `address` (required): Full UK property address
- `postcode` (optional): UK postcode - recommended for Land Registry data
- `strategy` (optional): 
  - `"priority"` (default): Tries sources sequentially, returns first success
  - `"all"`: Queries all sources in parallel and aggregates data

**Response:**
```json
{
  "success": true,
  "address": "Baker Street, London",
  "sources_queried": ["land_registry", "zoopla", "onthemarket", "rightmove"],
  "successful_sources": ["zoopla", "land_registry"],
  "failed_sources": [
    {"source": "rightmove", "error": "Bot protection"}
  ],
  "data": {
    "current_price": "£950,000",
    "current_price_source": "zoopla",
    "last_sale_price": "£750,000",
    "last_sale_date": "2020-03-15",
    "sale_history_source": "Land Registry (Official)",
    "property_type": "3 bedroom house",
    "tenure": "Freehold",
    "bedrooms": 3,
    "agent": "Example Estate Agents",
    "features": ["Garden", "Parking"],
    "listing_url": "https://..."
  },
  "raw_sources": {
    "zoopla": { /* full zoopla response */ },
    "land_registry": { /* full land registry response */ }
  }
}
```

### 2. Land Registry (Official Government Data)

**POST /api/sources/land-registry**

Most reliable source for historical sale data.

```bash
curl -X POST http://localhost:5001/api/sources/land-registry \
  -H "Content-Type: application/json" \
  -d '{"postcode": "SW1A 2AA"}'
```

**Response:**
```json
{
  "success": true,
  "source": "Land Registry (Official Gov Data)",
  "postcode": "SW1A 2AA",
  "last_sale_price": 750000,
  "last_sale_date": "2020-03-15",
  "sale_history": [
    {
      "price": 750000,
      "date": "2020-03-15",
      "property_type": "Terraced",
      "tenure": "Freehold",
      "new_build": false,
      "address": "10 Downing Street, Westminster"
    }
  ],
  "total_transactions": 15
}
```

### 3. Zoopla

**POST /api/sources/zoopla**

```bash
curl -X POST http://localhost:5001/api/sources/zoopla \
  -H "Content-Type: application/json" \
  -d '{"address": "Baker Street, London"}'
```

### 4. OnTheMarket

**POST /api/sources/onthemarket**

```bash
curl -X POST http://localhost:5001/api/sources/onthemarket \
  -H "Content-Type: application/json" \
  -d '{"address": "Oxford Street, London"}'
```

### 5. Rightmove

**POST /api/sources/rightmove**

```bash
curl -X POST http://localhost:5001/api/sources/rightmove \
  -H "Content-Type: application/json" \
  -d '{"address": "Piccadilly, London"}'
```

### 6. Batch Processing

**POST /api/batch-properties**

Query multiple properties at once.

```bash
curl -X POST http://localhost:5001/api/batch-properties \
  -H "Content-Type: application/json" \
  -d '{
    "addresses": [
      "Baker Street, London",
      "Oxford Street, London"
    ],
    "postcodes": ["NW1 6XE", "W1D 1BS"],
    "strategy": "priority"
  }'
```

## 🔧 Python Usage

### Multi-Source Search

```python
from scraper.multi_source_scraper import search_property_multi_source

# Priority strategy (fast, returns first success)
data = search_property_multi_source(
    address="Baker Street, London",
    postcode="NW1 6XE",
    strategy="priority"
)

# All sources strategy (comprehensive, cross-validated)
data = search_property_multi_source(
    address="Baker Street, London",
    postcode="NW1 6XE",
    strategy="all"
)
```

### Individual Sources

```python
from scraper import (
    search_land_registry,
    search_zoopla,
    search_onthemarket,
    scrape_property  # Rightmove
)

# Land Registry (requires postcode)
lr_data = search_land_registry("NW1 6XE")

# Zoopla
zoopla_data = search_zoopla("Baker Street, London")

# OnTheMarket
otm_data = search_onthemarket("Baker Street, London")

# Rightmove
rm_data = scrape_property("Baker Street, London")
```

## 📊 Data Fields

All scrapers aim to return:

| Field | Description | Source Priority |
|-------|-------------|-----------------|
| `current_price` | Current listing price | Zoopla > OnTheMarket > Rightmove |
| `last_sale_price` | Most recent sale price | Land Registry > Others |
| `last_sale_date` | Date of last sale | Land Registry > Others |
| `sale_history` | Historical sales | Land Registry (official) |
| `property_type` | Type of property | Cross-validated |
| `tenure` | Freehold/Leasehold | Cross-validated |
| `bedrooms` | Number of bedrooms | Cross-validated |
| `features` | Property features | Best available |
| `agent` | Estate agent | Current listing |
| `listing_url` | URL to listing | Current listing |

## ⚠️ Important Notes

### Land Registry
- ✅ **Most reliable** - Official UK government data
- ✅ Free and open data
- ⚠️ Requires **postcode** (not full address)
- ⚠️ Only historical sales (not current listings)
- 📅 Updated quarterly

### Zoopla
- ✅ Major portal with good data coverage
- ✅ Both current listings and sold prices
- ⚠️ May have bot protection
- 💡 Best for current market prices

### OnTheMarket
- ✅ Owned by estate agents - reliable listings
- ✅ Good property details
- ⚠️ May have bot protection
- 💡 Good for property features

### Rightmove
- ✅ Largest UK property portal
- ❌ **Strong bot protection** - may block requests
- ⚠️ Most likely to fail
- �� Use as fallback only

## 🎯 Recommended Usage

**For Historical Sale Data:**
```python
# Use Land Registry - most reliable
data = search_land_registry("SW1A 2AA")
```

**For Current Listings:**
```python
# Use priority strategy - tries Zoopla first
data = search_property_multi_source(
    address="Your Address",
    strategy="priority"
)
```

**For Maximum Data:**
```python
# Use all sources strategy
data = search_property_multi_source(
    address="Your Address",
    postcode="POSTCODE",
    strategy="all"
)
# Returns aggregated and cross-validated data from all sources
```

## 🚦 Status

| Source | Status | Reliability |
|--------|--------|-------------|
| Land Registry | ✅ Working | ⭐⭐⭐⭐⭐ Official Gov Data |
| Zoopla | ⚠️ May be blocked | ⭐⭐⭐⭐ Major portal |
| OnTheMarket | ⚠️ May be blocked | ⭐⭐⭐⭐ Agent-owned |
| Rightmove | ❌ Likely blocked | ⭐⭐⭐ Has strong protection |

## 🔐 Bot Protection Notes

UK property portals have increasingly sophisticated bot protection:

1. **Land Registry** - ✅ Open data, no protection
2. **Zoopla** - May work with tls-client
3. **OnTheMarket** - May work with tls-client
4. **Rightmove** - Strong Cloudflare protection

**For production use**, consider:
- Using official APIs (paid)
- Implementing proxy rotation
- Adding delays between requests
- Using browser automation (Playwright/Selenium)

## 📞 Support

For issues or questions about the scraper, check:
- Individual source scrapers in `/backend/scraper/`
- API implementation in `/backend/scraper_api.py`
- Multi-source aggregation in `/backend/scraper/multi_source_scraper.py`
