# Complete Test Results: 28 Crimple Meadows, Pannal, Harrogate HG3 1EN

**Test Date:** 2026-01-31 13:35:00  
**Address:** 28 Crimple Meadows, Pannal, Harrogate  
**Postcode:** HG3 1EN  
**Location:** Pannal, Harrogate, North Yorkshire, England

---

## Test Summary

**10 Tests Executed Across 3 Tiers:**
- TIER 1: Official APIs (3 tests)
- TIER 2: Browser Automation (3 tests)
- TIER 3: Advanced TLS Scraping (3 tests)
- Aggregated: Multi-Source (1 test)

---

## Detailed Results


### [1/10] Scansan API - Basic Search

```json
{
    "error": "API returned status 401",
    "source": "Scansan API",
    "success": false
}
```

### [2/10] Scansan API - Comprehensive

```json
{
    "error": "API returned status 401",
    "source": "Scansan API",
    "success": false
}
```

### [3/10] Land Registry (UK Government)

```json
{
    "error": "No transactions found for this postcode",
    "postcode": "HG31EN",
    "source": "Land Registry",
    "success": false
}
```

### [4/10] Playwright Rightmove (Browser)

```json
```

### [5/10] Playwright Zoopla (Browser)

```json
```

### [6/10] Playwright OnTheMarket (Browser)

```json
```

### [7/10] Enhanced Rightmove (TLS)

```json
{
    "address": "28 Crimple Meadows, Pannal, Harrogate",
    "error": "Search failed with status code 400",
    "success": false
}
```

### [8/10] Enhanced Zoopla (TLS)

```json
{
    "address": "28 Crimple Meadows, Pannal, Harrogate",
    "error": "Search failed with status 308",
    "source": "Zoopla",
    "success": false
}
```

### [9/10] Enhanced OnTheMarket (TLS)

```json
{
    "address": "28 Crimple Meadows, Pannal, Harrogate",
    "error": "Search failed with status 303",
    "source": "OnTheMarket",
    "success": false
}
```

### [10/10] Multi-Source Aggregator

```json
{
    "address": "28 Crimple Meadows, Pannal, Harrogate",
    "data": {},
    "error": "All sources failed",
    "failed_sources": [
        {
            "error": "No transactions found for this postcode",
            "source": "land_registry"
        },
        {
            "error": "Search failed with status 308",
            "source": "zoopla"
        },
        {
            "error": "Search failed with status 303",
            "source": "onthemarket"
        },
        {
            "error": "Search failed with status code 400",
            "source": "rightmove"
        }
    ],
    "sources_queried": [
        "land_registry",
        "zoopla",
        "onthemarket",
        "rightmove"
    ],
    "success": false,
    "successful_sources": []
}
```
