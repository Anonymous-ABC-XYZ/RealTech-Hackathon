# Property Scraper API - Quick Start Guide

## Installation

1. **Install dependencies:**
```bash
cd backend
pip install -r requirements.txt
```

## Starting the API Server

```bash
python scraper_api.py
```

The server will start on `http://localhost:5001`

## Quick Test

### Using curl (Address in header):
```bash
curl -X GET http://localhost:5001/api/property \
  -H "Address: Baker Street, London"
```

### Using curl (Address in body):
```bash
curl -X POST http://localhost:5001/api/property \
  -H "Content-Type: application/json" \
  -d '{"address": "Oxford Street, London"}'
```

### Batch request:
```bash
curl -X POST http://localhost:5001/api/batch-properties \
  -H "Content-Type: application/json" \
  -d '{
    "addresses": [
      "10 Downing Street, London",
      "Baker Street, London"
    ]
  }'
```

## Testing

Run the test suite:
```bash
./test_api.sh
```

## Python Example

```python
from scraper.rightmove_scraper import scrape_property

# Get property data
data = scrape_property("10 Downing Street, London SW1A 2AA")

if data["success"]:
    print(f"Current Price: {data.get('current_price')}")
    print(f"Property Type: {data.get('property_type')}")
    print(f"Tenure: {data.get('tenure')}")
    print(f"Last Sale: {data.get('last_sale_price')} on {data.get('last_sale_date')}")
```

## Response Format

```json
{
  "success": true,
  "address": "10 Downing Street, London SW1A 2AA",
  "current_listing": true,
  "current_price": "£950,000",
  "property_type": "3 bedroom terraced house",
  "bedrooms": 3,
  "tenure": "Freehold",
  "added_on": "12/01/2026",
  "listing_url": "https://www.rightmove.co.uk/properties/...",
  "agent": "Example Estate Agents",
  "features": ["Garden", "Parking", "Recently renovated"],
  "last_sale_price": "£750,000",
  "last_sale_date": "March 2020",
  "sale_history": [
    {
      "price": "£750,000",
      "date": "March 2020"
    }
  ]
}
```

## Key Features

✅ **Current Listing Data** - Price, agent, features for properties on sale  
✅ **Historical Data** - Last sale price and date  
✅ **Property Details** - Tenure (freehold/leasehold), bedrooms, type  
✅ **TLS Client** - Bypasses bot detection  
✅ **Multiple Endpoints** - GET with headers or POST with JSON body  
✅ **Batch Processing** - Query multiple properties at once  

## Documentation

See `/backend/scraper/README.md` for full API documentation.

## Troubleshooting

**Port already in use?**
```bash
# Change port in scraper_api.py, line: app.run(debug=True, host='0.0.0.0', port=5001)
```

**Dependencies not installed?**
```bash
pip install tls-client beautifulsoup4 lxml flask flask-cors
```

**Scraper not finding data?**
- Rightmove may have updated their HTML structure
- Check the property address is valid and in UK
- Try with a different, well-known address first
