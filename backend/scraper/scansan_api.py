"""
Scansan API Integration
Property data from Scansan.com - UK property data service
Documentation: https://docs.scansan.com/v1/docs
"""

import requests
from typing import Dict, Optional, List
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()


class ScansanAPIClient:
    """
    Client for Scansan API - UK Property Data Service.
    Provides comprehensive property information including:
    - Current valuations
    - Sale history
    - Property details
    - Market trends
    - Area statistics
    """
    
    def __init__(self, api_key: Optional[str] = None):
        """
        Initialize Scansan API client.
        
        Args:
            api_key: Scansan API key (or set SCANSAN_API_KEY env variable)
        """
        self.api_key = api_key or os.getenv('SCANSAN_API_KEY')
        if not self.api_key:
            raise ValueError("Scansan API key required. Set SCANSAN_API_KEY environment variable.")
        
        self.base_url = "https://api.scansan.com/v1"
        self.headers = {
            'Authorization': f'Bearer {self.api_key}',
            'Content-Type': 'application/json',
            'Accept': 'application/json'
        }
    
    def search_property(self, address: str = None, postcode: str = None) -> Dict:
        """
        Search for property by address or postcode.
        
        Args:
            address: Full property address
            postcode: UK postcode
            
        Returns:
            Dictionary with property data
        """
        try:
            # Construct search parameters
            params = {}
            if address:
                params['address'] = address
            if postcode:
                params['postcode'] = postcode
            
            # Make API request
            response = requests.get(
                f"{self.base_url}/property/search",
                headers=self.headers,
                params=params,
                timeout=30
            )
            
            if response.status_code == 200:
                data = response.json()
                return self._format_property_data(data)
            else:
                return {
                    "success": False,
                    "error": f"API returned status {response.status_code}",
                    "source": "Scansan API"
                }
                
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "source": "Scansan API"
            }
    
    def get_property_details(self, property_id: str) -> Dict:
        """
        Get detailed information for a specific property.
        
        Args:
            property_id: Unique property identifier
            
        Returns:
            Detailed property information
        """
        try:
            response = requests.get(
                f"{self.base_url}/property/{property_id}",
                headers=self.headers,
                timeout=30
            )
            
            if response.status_code == 200:
                data = response.json()
                return self._format_property_data(data)
            else:
                return {
                    "success": False,
                    "error": f"API returned status {response.status_code}",
                    "source": "Scansan API"
                }
                
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "source": "Scansan API"
            }
    
    def get_sale_history(self, property_id: str) -> Dict:
        """
        Get sale history for a property.
        
        Args:
            property_id: Unique property identifier
            
        Returns:
            Sale history data
        """
        try:
            response = requests.get(
                f"{self.base_url}/property/{property_id}/sales",
                headers=self.headers,
                timeout=30
            )
            
            if response.status_code == 200:
                return {
                    "success": True,
                    "sale_history": response.json(),
                    "source": "Scansan API"
                }
            else:
                return {
                    "success": False,
                    "error": f"API returned status {response.status_code}"
                }
                
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }
    
    def get_valuation(self, property_id: str) -> Dict:
        """
        Get current property valuation.
        
        Args:
            property_id: Unique property identifier
            
        Returns:
            Valuation data
        """
        try:
            response = requests.get(
                f"{self.base_url}/property/{property_id}/valuation",
                headers=self.headers,
                timeout=30
            )
            
            if response.status_code == 200:
                return {
                    "success": True,
                    "valuation": response.json(),
                    "source": "Scansan API"
                }
            else:
                return {
                    "success": False,
                    "error": f"API returned status {response.status_code}"
                }
                
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }
    
    def get_area_stats(self, postcode: str) -> Dict:
        """
        Get area statistics for a postcode.
        
        Args:
            postcode: UK postcode
            
        Returns:
            Area statistics
        """
        try:
            response = requests.get(
                f"{self.base_url}/area/stats",
                headers=self.headers,
                params={'postcode': postcode},
                timeout=30
            )
            
            if response.status_code == 200:
                return {
                    "success": True,
                    "area_stats": response.json(),
                    "source": "Scansan API"
                }
            else:
                return {
                    "success": False,
                    "error": f"API returned status {response.status_code}"
                }
                
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }
    
    def _format_property_data(self, api_data: Dict) -> Dict:
        """
        Format Scansan API response to match our standard format.
        
        Args:
            api_data: Raw API response
            
        Returns:
            Formatted property data
        """
        # Standard format matching other scrapers
        formatted = {
            "success": True,
            "source": "Scansan API",
            "current_price": None,
            "current_listing": None,
            "last_sale_price": None,
            "last_sale_date": None,
            "property_type": None,
            "tenure": None,
            "bedrooms": None,
            "bathrooms": None,
            "features": [],
            "sale_history": [],
            "valuation": {},
            "area_stats": {},
            "raw_data": api_data
        }
        
        # Extract data based on Scansan API structure
        # Note: Adjust these fields based on actual API response
        if isinstance(api_data, dict):
            # Current listing info
            if 'price' in api_data:
                formatted['current_price'] = api_data.get('price')
                formatted['current_listing'] = True
            
            # Property details
            formatted['property_type'] = api_data.get('property_type')
            formatted['tenure'] = api_data.get('tenure')
            formatted['bedrooms'] = api_data.get('bedrooms')
            formatted['bathrooms'] = api_data.get('bathrooms')
            
            # Sale history
            if 'sales' in api_data and isinstance(api_data['sales'], list):
                formatted['sale_history'] = api_data['sales']
                if api_data['sales']:
                    latest = api_data['sales'][0]
                    formatted['last_sale_price'] = latest.get('price')
                    formatted['last_sale_date'] = latest.get('date')
            
            # Features
            if 'features' in api_data:
                formatted['features'] = api_data.get('features', [])
            
            # Valuation
            if 'valuation' in api_data:
                formatted['valuation'] = api_data.get('valuation')
            
            # Area statistics
            if 'area_stats' in api_data:
                formatted['area_stats'] = api_data.get('area_stats')
            
            # Address
            if 'address' in api_data:
                formatted['address'] = api_data.get('address')
            if 'postcode' in api_data:
                formatted['postcode'] = api_data.get('postcode')
        
        return formatted


def search_scansan(address: str = None, postcode: str = None, api_key: str = None) -> Dict:
    """
    Convenience function to search Scansan API.
    
    Args:
        address: Property address
        postcode: UK postcode
        api_key: Scansan API key (optional if set in env)
        
    Returns:
        Property data dictionary
    """
    try:
        client = ScansanAPIClient(api_key=api_key)
        return client.search_property(address=address, postcode=postcode)
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "source": "Scansan API"
        }


def get_comprehensive_property_data(address: str = None, postcode: str = None, 
                                    api_key: str = None) -> Dict:
    """
    Get comprehensive property data from Scansan including all available information.
    
    Args:
        address: Property address
        postcode: UK postcode
        api_key: Scansan API key
        
    Returns:
        Comprehensive property data
    """
    try:
        client = ScansanAPIClient(api_key=api_key)
        
        # Search for property
        property_data = client.search_property(address=address, postcode=postcode)
        
        if property_data.get('success') and 'property_id' in property_data.get('raw_data', {}):
            property_id = property_data['raw_data']['property_id']
            
            # Get additional details
            sale_history = client.get_sale_history(property_id)
            valuation = client.get_valuation(property_id)
            
            # Merge data
            if sale_history.get('success'):
                property_data['sale_history'] = sale_history.get('sale_history', [])
            
            if valuation.get('success'):
                property_data['valuation'] = valuation.get('valuation', {})
            
            # Get area stats if postcode available
            if postcode:
                area_stats = client.get_area_stats(postcode)
                if area_stats.get('success'):
                    property_data['area_stats'] = area_stats.get('area_stats', {})
        
        return property_data
        
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "source": "Scansan API"
        }
