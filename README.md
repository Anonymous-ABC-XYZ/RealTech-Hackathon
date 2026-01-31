# RealTech Property Price Predictor

A modern, sleek property price prediction web application built for the RealTech Hackathon 2026.

![RealTech](https://img.shields.io/badge/RealTech-Hackathon%202026-19747E)

## 🎨 Design

Inspired by Stripe's clean, professional aesthetic with a custom color palette:

- **Soft Mint Green**: `#D1E8E2`
- **Dark Cyan**: `#19747E`
- **Light Blue**: `#A9D6E5`
- **Platinum**: `#E2E2E2`

## 🏗️ Project Structure

```
RealTech-Hackathon/
├── backend/
│   ├── app.py                  # Flask API server
│   ├── requirements.txt        # Python dependencies
│   ├── run_scraper.py          # CLI tool for scraping
│   └── scraper/
│       ├── land_registry_scraper.py   # UK Land Registry API
│       ├── rightmove_scraper.py       # Rightmove scraper
│       ├── zoopla_scraper.py          # Zoopla scraper
│       └── multi_source_scraper.py    # Aggregates sources
├── frontend/
│   ├── src/
│   │   ├── app/
│   │   │   ├── layout.tsx
│   │   │   ├── page.tsx
│   │   │   └── globals.css
│   │   └── components/
│   │       ├── Header.tsx
│   │       ├── MapSection.tsx
│   │       └── PropertyPanel.tsx
│   ├── next.config.js
│   ├── tailwind.config.js
│   └── package.json
└── README.md
```

## 🚀 Getting Started

### Prerequisites

- Node.js 18+ and npm
- Python 3.9+
- pip

### Backend Setup

```bash
cd backend
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
python app.py
```

The backend will run on `http://localhost:5000`

### Frontend Setup

```bash
cd frontend
npm install
npm run dev
```

The frontend will run on `http://localhost:3000`

---

## 🏠 Land Registry Data Scraper

Access official UK property transaction data from HM Land Registry.

### Quick Start

```python
from scraper.land_registry_scraper import LandRegistryScraper, search_land_registry

# Create scraper
scraper = LandRegistryScraper()

# Search by street (most reliable)
result = scraper.search_by_street("ROLAND GARDENS", "LONDON")

# Search specific address
result = scraper.search_by_address("14 Roland Gardens", town="LONDON")

# Convenience function
result = search_land_registry("BAKER STREET", town="LONDON")

# Use results
if result['success']:
    for t in result['transactions'][:5]:
        print(f"{t['address']}: £{t['price']:,} ({t['date']})")
    print(f"Average: £{result['statistics']['average_price']:,}")
```

### Response Format

```json
{
  "success": true,
  "source": "land_registry",
  "transactions": [
    {
      "price": 1250000,
      "date": "15 March 2023",
      "property_type": "Flat-maisonette",
      "tenure": "Leasehold",
      "new_build": false,
      "address": "FLAT 3, 14, ROLAND GARDENS, LONDON, SW7 3PH",
      "paon": "14",
      "street": "ROLAND GARDENS",
      "town": "LONDON",
      "postcode": "SW7 3PH"
    }
  ],
  "statistics": {
    "count": 50,
    "average_price": 602590,
    "min_price": 22000,
    "max_price": 5550000,
    "median_price": 310000
  }
}
```

### API Methods

| Method | Description | Example |
|--------|-------------|---------|
| `search_by_street(street, town)` | Search by street | `search_by_street("BAKER STREET", "LONDON")` |
| `search_by_address(address, town)` | Search address | `search_by_address("14 Roland Gardens", town="LONDON")` |
| `search_by_postcode(postcode)` | Search postcode | `search_by_postcode("SW7 3RP")` |
| `search_land_registry(query, town)` | Auto-detect type | `search_land_registry("OXFORD STREET", town="LONDON")` |

### Command Line Usage

```bash
cd backend

# Default test (Roland Gardens, London)
python run_scraper.py

# Search any street
python run_scraper.py "OXFORD STREET" "LONDON"

# Search specific address
python run_scraper.py "10 Downing Street" address "LONDON"
```

### Data Coverage

| Region | Coverage |
|--------|----------|
| England | ✅ Full (from 1995) |
| Wales | ✅ Full (from 1995) |
| Scotland | ❌ Use Registers of Scotland |
| N. Ireland | ❌ Use Land & Property Services |

---

## 📄 Flask API Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/health` | GET | Health check |
| `/api/predict` | POST | Price prediction (placeholder) |
| `/api/area-data` | GET | Area data for coordinates |

---

## 📱 Features

- **Interactive Apple Maps**: Click to select any location
- **Address Search**: Search for properties by address
- **AI Price Prediction**: Get instant price predictions
- **Area Insights**: Demographics, amenities, transport data
- **Mobile Responsive**: Works on all devices
- **Stripe-inspired UI**: Clean, modern design

## 🛠️ Tech Stack

### Frontend
- Next.js 14 (App Router)
- TypeScript
- Tailwind CSS
- Apple MapKit JS

### Backend
- Flask
- Flask-CORS
- Requests

## 📝 License

MIT License - Built for RealTech Hackathon 2026
