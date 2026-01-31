# Rightmove Property Scraper API

A Flask-based API server that scrapes UK residential and commercial property data from Rightmove using tls-client to bypass bot detection.

## Features

- **Current Listing Data**: Get current price for properties on sale
- **Historical Data**: Last sale price and date
- **Property Details**: Tenure (freehold/leasehold), bedrooms, property type
- **Additional Info**: Estate agent, property features, descriptions
- **Batch Processing**: Query multiple properties in one request

## Installation

```bash
pip install -r requirements.txt
```

## Running the API Server

```bash
cd backend
python scraper_api.py
```

The server will start on `http://localhost:5001`

## API Endpoints

### 1. GET /api/property

Get property data using address in header.

**Request:**
```bash
curl -X GET http://localhost:5001/api/property \
  -H "Address: 10 Downing Street, London SW1A 2AA"
```

**Response:**
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
  "features": [
    "Garden",
    "Parking",
    "Recently renovated"
  ],
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

### 2. POST /api/property

Get property data using JSON body.

**Request:**
```bash
curl -X POST http://localhost:5001/api/property \
  -H "Content-Type: application/json" \
  -d '{"address": "10 Downing Street, London SW1A 2AA"}'
```

### 3. POST /api/batch-properties

Get data for multiple properties.

**Request:**
```bash
curl -X POST http://localhost:5001/api/batch-properties \
  -H "Content-Type: application/json" \
  -d '{
    "addresses": [
      "10 Downing Street, London SW1A 2AA",
      "1 Palace Street, London SW1E 5HX"
    ]
  }'
```

**Response:**
```json
{
  "success": true,
  "count": 2,
  "results": [
    { /* property 1 data */ },
    { /* property 2 data */ }
  ]
}
```

### 4. GET /health

Health check endpoint.

**Request:**
```bash
curl http://localhost:5001/health
```

**Response:**
```json
{
  "status": "healthy",
  "service": "property-scraper-api"
}
```

## Data Fields Returned

| Field | Type | Description |
|-------|------|-------------|
| `success` | boolean | Whether the scrape was successful |
| `address` | string | The queried address |
| `current_listing` | boolean | Whether property is currently for sale |
| `current_price` | string | Current listing price |
| `property_type` | string | Type of property (e.g., "3 bedroom house") |
| `bedrooms` | number | Number of bedrooms |
| `tenure` | string | "Freehold" or "Leasehold" |
| `added_on` | string | Date listing was added |
| `listing_url` | string | URL to the property listing |
| `agent` | string | Estate agent name |
| `features` | array | List of property features |
| `description` | string | Property description (truncated) |
| `last_sale_price` | string | Most recent sale price |
| `last_sale_date` | string | Date of most recent sale |
| `sale_history` | array | Full sale history |

## Direct Python Usage

You can also use the scraper directly in Python:

```python
from scraper.rightmove_scraper import scrape_property

# Get property data
data = scrape_property("10 Downing Street, London SW1A 2AA")
print(data)
```

## Error Handling

The API returns appropriate HTTP status codes:

- `200`: Success
- `400`: Bad request (missing address)
- `404`: Property not found
- `500`: Server error

Error responses include:
```json
{
  "success": false,
  "error": "Error message here",
  "address": "queried address"
}
```

## Notes

- The scraper uses tls-client to avoid bot detection
- Rightmove may update their HTML structure, requiring updates to selectors
- Rate limiting is recommended for production use
- Consider implementing caching for frequently queried addresses
