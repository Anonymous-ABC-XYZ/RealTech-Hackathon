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
│   ├── app.py              # Flask API server
│   └── requirements.txt    # Python dependencies
├── frontend/
│   ├── src/
│   │   ├── app/
│   │   │   ├── layout.tsx      # Root layout
│   │   │   ├── page.tsx        # Home page
│   │   │   └── globals.css     # Global styles
│   │   ├── components/
│   │   │   ├── Header.tsx      # Navigation header
│   │   │   ├── MapSection.tsx  # Apple Maps integration
│   │   │   └── PropertyPanel.tsx # Property data display
│   │   └── types/
│   │       └── index.ts        # TypeScript types
│   ├── next.config.js
│   ├── tailwind.config.js
│   ├── tsconfig.json
│   └── package.json
└── README.md
```

## 🚀 Getting Started

### Prerequisites

- Node.js 18+ and npm
- Python 3.9+
- pip
- Apple Developer account (for MapKit JS token)

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
```

Create a `.env.local` file with your MapKit JS token:

```env
NEXT_PUBLIC_MAPKIT_TOKEN=your_mapkit_js_token_here
NEXT_PUBLIC_API_URL=http://localhost:5000
```

Start the development server:

```bash
npm run dev
```

The frontend will run on `http://localhost:3000`

## 🗺️ Apple MapKit JS Setup

1. Go to [Apple Developer Portal](https://developer.apple.com)
2. Navigate to Certificates, Identifiers & Profiles
3. Create a new Maps ID
4. Generate a MapKit JS key
5. Create a JWT token for authentication
6. Add the token to your `.env.local` file

## 🐍 Python Backend Structure

The Flask backend is designed to be extended with your prediction model:

```python
# backend/app.py

def predict_property_price(address: str, lat: float, lng: float) -> dict:
    """
    Main prediction function - Implement your model here
    
    Args:
        address: Full address string
        lat: Latitude coordinate
        lng: Longitude coordinate
    
    Returns:
        Dictionary containing prediction results
    """
    # TODO: Add your ML model here
    pass

def get_area_data(lat: float, lng: float) -> dict:
    """
    Fetch area data that influences property prices
    
    TODO: Implement data fetching from external APIs
    """
    pass
```

## 📱 Features

- **Interactive Apple Maps**: Click to select any location
- **Address Search**: Search for properties by address
- **AI Price Prediction**: Get instant price predictions (placeholder)
- **Area Insights**: View demographics, amenities, transport, safety, and market trends
- **Mobile Responsive**: Fully responsive design for all devices
- **Stripe-inspired UI**: Clean, modern, and professional design

## 🛠️ Tech Stack

### Frontend
- **Next.js 14** - React framework with App Router
- **TypeScript** - Type safety
- **Tailwind CSS** - Utility-first styling
- **Apple MapKit JS** - Maps integration
- **Lucide React** - Icons

### Backend
- **Flask** - Python web framework
- **Flask-CORS** - Cross-origin resource sharing

## 📄 API Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/health` | GET | Health check |
| `/api/predict` | POST | Get price prediction for a location |
| `/api/area-data` | GET | Get area data for coordinates |

## 🎯 Next Steps

1. Implement the ML prediction model in `backend/app.py`
2. Add external API integrations for real area data
3. Set up production deployment
4. Add user authentication (optional)
5. Add property comparison feature (optional)

## 📝 License

MIT License - Built for RealTech Hackathon 2026
