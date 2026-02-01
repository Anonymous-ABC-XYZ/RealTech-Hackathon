from flask import Flask, request, jsonify
from flask_cors import CORS
import pandas as pd
import sys
import os

# Add root directory to path to import model
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from scraper.multi_source_scraper import search_property_multi_source
from scraper.land_registry_scraper import search_land_registry
from scraper.flood_risk_scraper import get_flood_risk

# Model imports
from uk_property_resilience_model_optimized import UKPropertyFuturePricePredictor, load_kaggle_data

# Playwright scrapers
from scraper.playwright_rightmove import scrape_rightmove_playwright

# Scansan API
from scraper.scansan_api import search_scansan

import logging
import re
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

app = Flask(__name__)
CORS(app)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Global Model Instance
resilience_model = None

def train_model_on_startup():
    """Train the future price predictor on startup using Enriched data"""
    global resilience_model
    try:
        logger.info("Initializing and training Future Price Predictor...")
        dataset_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'ml-dataset/kaggle_london_enriched.csv')
        
        # Fallback to original if enriched doesn't exist
        if not os.path.exists(dataset_path):
            logger.warning("Enriched dataset not found. Falling back to raw data (Model will lack risk sensitivity).")
            dataset_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'ml-dataset/kaggle_london_house_price_data.csv')

        # Load Data
        logger.info(f"Loading data from {dataset_path}...")
        transactions_df, _ = load_kaggle_data(dataset_path)
        
        if transactions_df is None:
            logger.error("Failed to load training data.")
            return

        # Train
        resilience_model = UKPropertyFuturePricePredictor(parallel_training=True)
        resilience_model.fit(transactions_df, postcode_coords_df=None, val_size=0.1)
        logger.info("Future Price Predictor trained and ready!")
        
    except Exception as e:
        logger.error(f"Error training model on startup: {e}")

@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint."""
    model_status = "active" if resilience_model else "inactive"
    return jsonify({
        "status": "healthy", 
        "service": "property-scraper-api",
        "model_status": model_status
    }), 200


@app.route('/api/predict_resilience', methods=['POST'])
def predict_resilience():
    """
    Predict Future Property Prices (1y, 3y, 5y).
    
    Steps:
    1. Scrape live risk data (Flood, Crime).
    2. Lookup historical sector trends (Growth, Volatility).
    3. Forecast future value.
    """
    if not resilience_model:
        return jsonify({"success": False, "error": "Model not loaded"}), 503
        
    data = request.get_json()
    postcode = data.get('postcode')
    
    if not postcode:
        return jsonify({"success": False, "error": "Postcode is required"}), 400

    logger.info(f"Predicting future prices for: {postcode}")
    
    try:
        # 1. Get Live Data (Flood Risk + Coords)
        scraper_data = search_property_multi_source(address=postcode, postcode=postcode)
        
        flood_data = scraper_data.get('data', {}).get('flood_risk', {})
        flood_score = flood_data.get('risk_score', 0)
        
        # 2. Get Historical Context
        sector = resilience_model.extract_postcode_sector(postcode)
        stats = resilience_model.get_sector_stats(sector)
        
        if not stats:
            # Fallback for unknown sector
            stats = resilience_model.default_stats
            current_price = 500000 # Default London price
        else:
            current_price = stats.get('current_price', 500000)
        
        # 3. Construct Input Vector
        # We start with the historical stats
        input_data = pd.DataFrame([stats])
        
        # Override with LIVE risk data
        input_data['flood_risk'] = flood_score
        # crime_rate placeholder until Scansan/Police API fully live
        if 'crime_rate' not in input_data:
            input_data['crime_rate'] = 5.0 
            
        # Add Market Regime (Assumption: 2026 is a recovery year = 0.3)
        input_data['market_regime'] = 0.3
            
        # Ensure all features exist
        for col in resilience_model.feature_names:
            if col not in input_data.columns:
                input_data[col] = 0.0
                
        # 4. Predict
        forecast = resilience_model.predict(current_price, input_data)
        
        return jsonify({
            "success": True,
            "postcode": postcode,
            "sector": sector,
            "current_valuation": {
                "value": int(current_price),
                "currency": "GBP"
            },
            "risk_factors": {
                "flood_risk_score": flood_score,
                "flood_risk_level": flood_data.get('risk_level', 'Unknown'),
                "historical_volatility": round(stats.get('volatility', 0) * 100, 2)
            },
            "forecasts": forecast['forecasts']
        })

    except Exception as e:
        logger.error(f"Prediction error: {e}")
        return jsonify({"success": False, "error": str(e)}), 500

@app.route('/api/property', methods=['GET'])
def get_property_data():
    """
    Get property data by address from multiple sources.
    
    Expected headers:
        Address: Full UK property address (required)
        Postcode: UK postcode (optional, recommended for Land Registry)
        Strategy: "all" or "priority" (optional, default: "priority")
        
    Returns:
        JSON response with aggregated property information from multiple sources
    """
    # Get parameters from headers
    address = request.headers.get('Address')
    postcode = request.headers.get('Postcode')
    strategy = request.headers.get('Strategy', 'priority')
    
    if not address:
        return jsonify({
            "success": False,
            "error": "Address header is required"
        }), 400
    
    logger.info(f"Scraping property data for address: {address} (strategy: {strategy})")
    
    try:
        # Use multi-source scraper
        property_data = search_property_multi_source(
            address=address,
            postcode=postcode,
            strategy=strategy
        )
        
        if property_data.get("success"):
            logger.info(f"Successfully scraped data from {len(property_data.get('successful_sources', []))} sources")
            return jsonify(property_data), 200
        else:
            logger.warning(f"Failed to scrape data for: {address}")
            return jsonify(property_data), 404
            
    except Exception as e:
        logger.error(f"Error scraping property: {str(e)}")
        return jsonify({
            "success": False,
            "error": f"Internal server error: {str(e)}",
            "address": address
        }), 500


@app.route('/api/property', methods=['POST'])
def get_property_data_post():
    """
    Get property data by address (POST method).
    
    Expected JSON body:
        {
            "address": "Full UK property address",
            "postcode": "SW1A 2AA" (optional),
            "strategy": "all" or "priority" (optional, default: priority)
        }
        
    Returns:
        JSON response with aggregated property information from multiple sources
    """
    data = request.get_json()
    
    if not data or 'address' not in data:
        return jsonify({
            "success": False,
            "error": "Request body must include 'address' field"
        }), 400
    
    address = data['address']
    postcode = data.get('postcode')
    strategy = data.get('strategy', 'priority')
    
    logger.info(f"Scraping property data for address: {address} (strategy: {strategy})")
    
    try:
        # Use multi-source scraper
        property_data = search_property_multi_source(
            address=address,
            postcode=postcode,
            strategy=strategy
        )
        
        if property_data.get("success"):
            logger.info(f"Successfully scraped data from {len(property_data.get('successful_sources', []))} sources")
            return jsonify(property_data), 200
        else:
            logger.warning(f"Failed to scrape data for: {address}")
            return jsonify(property_data), 404
            
    except Exception as e:
        logger.error(f"Error scraping property: {str(e)}")
        return jsonify({
            "success": False,
            "error": f"Internal server error: {str(e)}",
            "address": address
        }), 500


@app.route('/api/batch-properties', methods=['POST'])
def get_batch_properties():
    """
    Get property data for multiple addresses.
    
    Expected JSON body:
        {
            "addresses": ["address1", "address2", ...],
            "postcodes": ["postcode1", "postcode2", ...] (optional),
            "strategy": "all" or "priority" (optional)
        }
        
    Returns:
        JSON array with property information for each address
    """
    data = request.get_json()
    
    if not data or 'addresses' not in data:
        return jsonify({
            "success": False,
            "error": "Request body must include 'addresses' array"
        }), 400
    
    addresses = data['addresses']
    postcodes = data.get('postcodes', [])
    strategy = data.get('strategy', 'priority')
    
    if not isinstance(addresses, list):
        return jsonify({
            "success": False,
            "error": "'addresses' must be an array"
        }), 400
    
    logger.info(f"Batch scraping {len(addresses)} properties")
    
    results = []
    for i, address in enumerate(addresses):
        try:
            postcode = postcodes[i] if i < len(postcodes) else None
            property_data = search_property_multi_source(address, postcode, strategy)
            results.append(property_data)
        except Exception as e:
            results.append({
                "success": False,
                "error": str(e),
                "address": address
            })
    
    return jsonify({
        "success": True,
        "count": len(results),
        "results": results
    }), 200


@app.route('/api/sources/land-registry', methods=['GET', 'POST'])
def get_land_registry_data():
    """
    Get data specifically from Land Registry (Official Government Data).
    Most reliable source for historical sale prices.
    
    GET: Use 'Postcode' header
    POST: Use JSON body with 'postcode' field
    """
    if request.method == 'GET':
        postcode = request.headers.get('Postcode')
    else:
        data = request.get_json()
        postcode = data.get('postcode') if data else None
    
    if not postcode:
        return jsonify({
            "success": False,
            "error": "Postcode is required"
        }), 400
    
    try:
        result = search_land_registry(postcode)
        return jsonify(result), 200 if result.get("success") else 404
    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e),
            "source": "Land Registry"
        }), 500


# ============================================================
# SCANSAN API ENDPOINTS (Official Property Data API)
# ============================================================

@app.route('/api/scansan/search', methods=['GET', 'POST'])
def scansan_search():
    """
    Search properties using Scansan API.
    Official UK property data API - most reliable source.
    
    GET: Use 'Address' and/or 'Postcode' headers
    POST: Use JSON body with 'address' and/or 'postcode' fields
    """
    if request.method == 'GET':
        address = request.headers.get('Address')
        postcode = request.headers.get('Postcode')
    else:
        data = request.get_json()
        address = data.get('address') if data else None
        postcode = data.get('postcode') if data else None
    
    if not address and not postcode:
        return jsonify({
            "success": False,
            "error": "Address or postcode required"
        }), 400
    
    logger.info(f"Scansan API search: address={address}, postcode={postcode}")
    
    try:
        result = search_scansan(address=address, postcode=postcode)
        return jsonify(result), 200 if result.get("success") else 404
    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e),
            "source": "Scansan API"
        }), 500


@app.route('/api/scansan/comprehensive', methods=['GET', 'POST'])
def scansan_comprehensive():
    """
    Get comprehensive property data from Scansan API.
    Includes property details, sale history, valuation, and area statistics.
    
    GET: Use 'Address' and/or 'Postcode' headers
    POST: Use JSON body with 'address' and/or 'postcode' fields
    """
    if request.method == 'GET':
        address = request.headers.get('Address')
        postcode = request.headers.get('Postcode')
    else:
        data = request.get_json()
        address = data.get('address') if data else None
        postcode = data.get('postcode') if data else None
    
    if not address and not postcode:
        return jsonify({
            "success": False,
            "error": "Address or postcode required"
        }), 400
    
    logger.info(f"Scansan API comprehensive search: address={address}, postcode={postcode}")
    
    try:
        result = get_comprehensive_property_data(address=address, postcode=postcode)
        return jsonify(result), 200 if result.get("success") else 404
    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e),
            "source": "Scansan API"
        }), 500


# ============================================================
# PLAYWRIGHT-BASED ENDPOINTS (Real Browser Automation)
# ============================================================

@app.route('/api/playwright/rightmove', methods=['GET', 'POST'])
def get_rightmove_playwright():
    """
    Get data from Rightmove using Playwright (real browser).
    Bypasses all bot protection including Cloudflare.
    
    GET: Use 'Address' header
    POST: Use JSON body with 'address' field
    """
    if request.method == 'GET':
        address = request.headers.get('Address')
    else:
        data = request.get_json()
        address = data.get('address') if data else None
    
    if not address:
        return jsonify({
            "success": False,
            "error": "Address is required"
        }), 400
    
    logger.info(f"Scraping Rightmove with Playwright: {address}")
    
    try:
        result = scrape_rightmove_playwright(address, headless=True)
        return jsonify(result), 200 if result.get("success") else 404
    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e),
            "source": "Rightmove (Playwright)"
        }), 500


@app.errorhandler(404)
def not_found(error):
    return jsonify({
        "success": False,
        "error": "Endpoint not found"
    }), 404


@app.errorhandler(500)
def internal_error(error):
    return jsonify({
        "success": False,
        "error": "Internal server error"
    }), 500


if __name__ == '__main__':
    train_model_on_startup()
    app.run(debug=True, host='0.0.0.0', port=5001)