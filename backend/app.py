"""
Property Price Prediction API
Flask backend for the RealTech Hackathon project
"""

from flask import Flask, request, jsonify
from flask_cors import CORS
import json

app = Flask(__name__)
CORS(app)


# ============================================================
# PREDICTION MODEL - Add your Python prediction code here
# ============================================================

def predict_property_price(address: str, lat: float, lng: float) -> dict:
    """
    Main prediction function - Implement your model here
    
    Args:
        address: Full address string
        lat: Latitude coordinate
        lng: Longitude coordinate
    
    Returns:
        Dictionary containing prediction results and area data
    """
    # TODO: Implement your prediction model here
    # This is where your ML/AI prediction code will go
    
    # Placeholder response
    return {
        "predicted_price": 450000,
        "confidence": 0.85,
        "price_range": {
            "low": 420000,
            "high": 480000
        }
    }


def get_area_data(lat: float, lng: float) -> dict:
    """
    Fetch area data that influences property prices
    
    Args:
        lat: Latitude coordinate
        lng: Longitude coordinate
    
    Returns:
        Dictionary containing area statistics and features
    """
    # TODO: Implement data fetching logic here
    # This could include API calls to get demographic data, 
    # crime rates, school ratings, etc.
    
    # Placeholder data
    return {
        "demographics": {
            "population": 45000,
            "median_age": 34,
            "median_income": 65000
        },
        "amenities": {
            "schools_nearby": 5,
            "parks_nearby": 3,
            "restaurants_nearby": 28,
            "grocery_stores": 4
        },
        "transport": {
            "nearest_station": "0.3 miles",
            "bus_routes": 4,
            "walk_score": 78,
            "transit_score": 65
        },
        "safety": {
            "crime_index": 23,
            "safety_rating": "B+"
        },
        "market_trends": {
            "avg_price_sqft": 285,
            "yoy_appreciation": 4.2,
            "days_on_market": 21,
            "inventory_level": "Low"
        }
    }


# ============================================================
# API ROUTES
# ============================================================

@app.route('/api/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({"status": "healthy", "service": "property-prediction-api"})


@app.route('/api/predict', methods=['POST'])
def predict():
    """
    Predict property price for a given location
    
    Expected JSON body:
    {
        "address": "123 Main St, City, State",
        "lat": 51.5074,
        "lng": -0.1278
    }
    """
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({"error": "No data provided"}), 400
        
        address = data.get('address', '')
        lat = data.get('lat')
        lng = data.get('lng')
        
        if lat is None or lng is None:
            return jsonify({"error": "Latitude and longitude are required"}), 400
        
        # Get prediction
        prediction = predict_property_price(address, lat, lng)
        
        # Get area data
        area_data = get_area_data(lat, lng)
        
        response = {
            "success": True,
            "address": address,
            "coordinates": {"lat": lat, "lng": lng},
            "prediction": prediction,
            "area_data": area_data
        }
        
        return jsonify(response)
    
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route('/api/area-data', methods=['GET'])
def area_data():
    """
    Get area data for a specific location
    
    Query parameters:
    - lat: Latitude
    - lng: Longitude
    """
    try:
        lat = request.args.get('lat', type=float)
        lng = request.args.get('lng', type=float)
        
        if lat is None or lng is None:
            return jsonify({"error": "Latitude and longitude are required"}), 400
        
        data = get_area_data(lat, lng)
        
        return jsonify({
            "success": True,
            "coordinates": {"lat": lat, "lng": lng},
            "data": data
        })
    
    except Exception as e:
        return jsonify({"error": str(e)}), 500


if __name__ == '__main__':
    app.run(debug=True, port=5000)
