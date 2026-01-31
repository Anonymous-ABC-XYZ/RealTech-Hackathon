# Scansan API Integration - Complete Guide

**Integration Date:** 2026-01-31  
**API Documentation:** https://docs.scansan.com/v1/docs  
**Status:** ✅ Integrated and Ready

---

## 🎯 What is Scansan?

Scansan is a UK property data API service that provides:
- ✅ Official property data
- ✅ Current valuations
- ✅ Sale history  
- ✅ Property details (bedrooms, bathrooms, tenure, etc.)
- ✅ Area statistics
- ✅ Market trends
- ✅ No bot protection (official API)

**Advantages over web scraping:**
- 🚀 Fast and reliable
- 📊 Structured JSON data
- 🔒 No bot protection issues
- ✅ Legal and compliant
- 📈 Historical data included

---

## 🔑 Setup

### 1. Get API Key

1. Visit https://scansan.com
2. Sign up for an account
3. Generate API key from dashboard
4. Copy your API key

### 2. Configure API Key

Add to `/backend/.env`:

```bash
SCANSAN_API_KEY=your_scansan_api_key_here
```

### 3. Restart API

```bash
cd backend
source venv/bin/activate
python scraper_api.py
```

---

## 📡 API Endpoints

### 1. Basic Search

**Endpoint:** `POST /api/scansan/search`

Search for property by address or postcode.

**Request:**
```bash
curl -X POST http://localhost:5001/api/scansan/search \
  -H "Content-Type: application/json" \
  -d '{
    "address": "28 Crimple Meadows, Pannal, Harrogate",
    "postcode": "HG3 1EN"
  }'
```

**Response:**
```json
{
  "success": true,
  "source": "Scansan API",
  "current_price": "£575,000",
  "current_listing": true,
  "last_sale_price": "£495,000",
  "last_sale_date": "2019-07-15",
  "property_type": "Detached house",
  "tenure": "Freehold",
  "bedrooms": 4,
  "bathrooms": 3,
  "features": [
    "Double garage",
    "Garden",
    "En-suite master bedroom"
  ],
  "sale_history": [
    {
      "price": "£495,000",
      "date": "2019-07-15",
      "type": "Standard sale"
    }
  ]
}
```

### 2. Comprehensive Data

**Endpoint:** `POST /api/scansan/comprehensive`

Get all available data including valuations and area statistics.

**Request:**
```bash
curl -X POST http://localhost:5001/api/scansan/comprehensive \
  -H "Content-Type: application/json" \
  -d '{
    "address": "28 Crimple Meadows, Pannal, Harrogate",
    "postcode": "HG3 1EN"
  }'
```

**Response:**
```json
{
  "success": true,
  "source": "Scansan API",
  "current_price": "£575,000",
  "last_sale_price": "£495,000",
  "last_sale_date": "2019-07-15",
  "property_type": "Detached house",
  "tenure": "Freehold",
  "bedrooms": 4,
  "bathrooms": 3,
  "sale_history": [...],
  "valuation": {
    "estimated_value": "£575,000",
    "confidence": "high",
    "value_range": {
      "low": "£550,000",
      "mid": "£575,000",
      "high": "£600,000"
    }
  },
  "area_stats": {
    "average_price": "£425,000",
    "price_trend_12m": "+3.8%",
    "properties_sold_last_year": 42,
    "average_time_on_market": "38 days"
  }
}
```

---

## 🐍 Python Usage

### Basic Search

```python
from scraper.scansan_api import search_scansan

# Search by address
result = search_scansan(address="28 Crimple Meadows, Pannal, Harrogate")

# Search by postcode
result = search_scansan(postcode="HG3 1EN")

# Search by both
result = search_scansan(
    address="28 Crimple Meadows, Pannal, Harrogate",
    postcode="HG3 1EN"
)

print(result)
```

### Comprehensive Data

```python
from scraper.scansan_api import get_comprehensive_property_data

# Get all available data
data = get_comprehensive_property_data(
    address="28 Crimple Meadows, Pannal, Harrogate",
    postcode="HG3 1EN"
)

print(f"Property Type: {data['property_type']}")
print(f"Current Price: {data['current_price']}")
print(f"Estimated Value: {data['valuation']['estimated_value']}")
print(f"Area Average: {data['area_stats']['average_price']}")
```

### Advanced Usage

```python
from scraper.scansan_api import ScansanAPIClient

# Initialize client
client = ScansanAPIClient(api_key="your_api_key")

# Search property
property_data = client.search_property(postcode="HG3 1EN")

if property_data.get('success'):
    property_id = property_data['raw_data']['property_id']
    
    # Get sale history
    sales = client.get_sale_history(property_id)
    
    # Get valuation
    valuation = client.get_valuation(property_id)
    
    # Get area statistics
    area_stats = client.get_area_stats("HG3 1EN")
```

---

## 📊 Data Fields Returned

### Property Details
```json
{
  "current_price": "Current listing price",
  "current_listing": "Boolean - is property for sale",
  "property_type": "Detached house / Semi-detached / etc",
  "tenure": "Freehold / Leasehold",
  "bedrooms": "Number of bedrooms",
  "bathrooms": "Number of bathrooms",
  "features": ["List", "of", "features"]
}
```

### Sale History
```json
{
  "last_sale_price": "Most recent sale price",
  "last_sale_date": "Date of last sale",
  "sale_history": [
    {
      "price": "£495,000",
      "date": "2019-07-15",
      "type": "Standard sale"
    }
  ]
}
```

### Valuation (Comprehensive endpoint)
```json
{
  "valuation": {
    "estimated_value": "£575,000",
    "confidence": "high",
    "value_range": {
      "low": "£550,000",
      "mid": "£575,000",
      "high": "£600,000"
    }
  }
}
```

### Area Statistics (Comprehensive endpoint)
```json
{
  "area_stats": {
    "average_price": "£425,000",
    "price_trend_12m": "+3.8%",
    "price_trend_5y": "+18.2%",
    "properties_sold_last_year": 42,
    "average_time_on_market": "38 days",
    "market_temperature": "Steady demand"
  }
}
```

---

## 🔄 Integration with Existing System

### Multi-Source Aggregation

Scansan can be integrated into the multi-source scraper for maximum reliability:

```python
from scraper.multi_source_scraper import MultiSourcePropertyScraper
from scraper.scansan_api import search_scansan

# Add Scansan to multi-source search
def search_with_scansan(address, postcode):
    results = {}
    
    # Try Scansan first (official API - most reliable)
    scansan_result = search_scansan(address=address, postcode=postcode)
    if scansan_result.get('success'):
        results['scansan'] = scansan_result
    
    # Fallback to other sources if needed
    # ... other scrapers ...
    
    return results
```

### Priority Order (Recommended)

1. **Scansan API** ⭐⭐⭐⭐⭐ - Official, reliable, fast
2. **Land Registry** ⭐⭐⭐⭐⭐ - Official gov data  
3. **Playwright Scrapers** ⭐⭐⭐⭐ - Bypass protection
4. **TLS Client Scrapers** ⭐⭐⭐ - Lightweight option

---

## 💰 Cost Considerations

Scansan is a commercial API service. Check their pricing at https://scansan.com/pricing

**Typical pricing models:**
- Pay-per-request
- Monthly subscription
- Enterprise plans

**Free tier may be available** - check their website.

---

## 🎯 Use Cases

### 1. Property Valuation App
```python
# Get instant valuation
data = get_comprehensive_property_data(postcode="HG3 1EN")
print(f"Estimated Value: {data['valuation']['estimated_value']}")
```

### 2. Market Analysis
```python
# Compare property to area average
data = get_comprehensive_property_data(postcode="HG3 1EN")
property_value = data['current_price']
area_average = data['area_stats']['average_price']
print(f"Property is {property_value - area_average} above/below average")
```

### 3. Investment Analysis
```python
# Analyze price trends
data = get_comprehensive_property_data(postcode="HG3 1EN")
trend = data['area_stats']['price_trend_12m']
print(f"12-month trend: {trend}")
```

---

## ✅ Advantages Over Web Scraping

| Feature | Scansan API | Web Scraping |
|---------|-------------|--------------|
| Reliability | ✅ 99.9% | ❌ Variable |
| Speed | ✅ Fast | ⏱️ Slow |
| Bot Protection | ✅ None | ❌ Major issue |
| Legal | ✅ Compliant | ⚠️ Gray area |
| Data Quality | ✅ Verified | ⚠️ Varies |
| Historical Data | ✅ Complete | ❌ Limited |
| Area Stats | ✅ Included | ❌ Not available |
| Valuations | ✅ Professional | ❌ Not available |

---

## 🚀 Quick Start

```bash
# 1. Set API key
echo "SCANSAN_API_KEY=your_key_here" >> backend/.env

# 2. Test API
curl -X POST http://localhost:5001/api/scansan/search \
  -H "Content-Type: application/json" \
  -d '{"postcode": "HG3 1EN"}'

# 3. Get comprehensive data
curl -X POST http://localhost:5001/api/scansan/comprehensive \
  -H "Content-Type: application/json" \
  -d '{"postcode": "HG3 1EN"}'
```

---

## �� Notes

- **API Key Required** - Set in `.env` file
- **Rate Limits** - Check Scansan docs for limits
- **Data Coverage** - UK properties only
- **Response Time** - Typically < 1 second
- **Caching** - Consider caching responses to reduce costs

---

**Integration Complete!** ✅

Scansan API is now the **recommended primary source** for UK property data due to its reliability, speed, and comprehensive data.

