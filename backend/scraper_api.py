from flask import Flask, request, jsonify
from flask_cors import CORS
from scraper.rightmove_scraper import scrape_property
import logging

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
    Get property data by address.
    
    Expected header:
        Address: Full UK property address
        
    Returns:
        JSON response with property information including:
        - current_price: Current listing price if available
        - last_sale_price: Last sale price
        - last_sale_date: Date of last sale
        - tenure: Freehold/Leasehold
        - property_type: Type of property
        - bedrooms: Number of bedrooms
        - features: List of property features
        - agent: Estate agent information
        - and more...
    """
    # Get address from header
    address = request.headers.get('Address')
    
    if not address:
        return jsonify({
            "success": False,
            "error": "Address header is required"
        }), 400
    
    logger.info(f"Scraping property data for address: {address}")
    
    try:
        # Scrape property data
        property_data = scrape_property(address)
        
        if property_data.get("success"):
            logger.info(f"Successfully scraped data for: {address}")
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
            "address": "Full UK property address"
        }
        
    Returns:
        JSON response with property information
    """
    data = request.get_json()
    
    if not data or 'address' not in data:
        return jsonify({
            "success": False,
            "error": "Request body must include 'address' field"
        }), 400
    
    address = data['address']
    logger.info(f"Scraping property data for address: {address}")
    
    try:
        # Scrape property data
        property_data = scrape_property(address)
        
        if property_data.get("success"):
            logger.info(f"Successfully scraped data for: {address}")
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
            "addresses": ["address1", "address2", ...]
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
    
    if not isinstance(addresses, list):
        return jsonify({
            "success": False,
            "error": "'addresses' must be an array"
        }), 400
    
    logger.info(f"Batch scraping {len(addresses)} properties")
    
    results = []
    for address in addresses:
        try:
            property_data = scrape_property(address)
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
