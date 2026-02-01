from flask import Flask, request, jsonify
from flask_cors import CORS
from scraper.multi_source_scraper import search_property_multi_source
from scraper.land_registry_scraper import search_land_registry

# Playwright scrapers
from scraper.playwright_rightmove import scrape_rightmove_playwright

# Scansan API
from scraper.scansan_api import search_scansan, get_comprehensive_property_data

import logging
import re
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

app = Flask(__name__)
CORS(app)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint."""
    return jsonify({"status": "healthy", "service": "property-scraper-api"}), 200


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
    app.run(debug=True, host='0.0.0.0', port=5001)