"""
Scansan API Client

A comprehensive Python client for the Scansan Property Data API.
Supports all available endpoints for area, postcode, district, and property data.

Usage:
    from scraper.scansan_api import ScansanAPI
    
    api = ScansanAPI()  # Uses SCANSAN_API_KEY from .env
    result = api.get_area_summary("SW7 3RP")
"""

import requests
from typing import Dict, Optional, Any, List
import os
from dotenv import load_dotenv
from urllib.parse import quote
import json
import time

load_dotenv()


class ScansanAPI:
    """
    Client for Scansan Property Data API.
    
    Supports all available endpoints:
    - Area Codes: search, summary, rent/sale listings, crime
    - Postcodes: sale history, classification, addresses, regeneration, 
                 valuations, energy, census, amenities, LHA
    - Districts: growth, rent/sale demand
    - Properties: planning, addresses, energy
    
    Rate limited to avoid 429 errors (1s delay between requests).
    """
    
    BASE_URL = "https://api.scansan.com/v1"
    
    def __init__(self, api_key: Optional[str] = None, rate_limit_delay: float = 1.0):
        """
        Initialize Scansan API client.
        
        Args:
            api_key: Scansan API key (defaults to SCANSAN_API_KEY from .env)
            rate_limit_delay: Delay between requests in seconds (default 1.0s)
        """
        self.api_key = api_key or os.getenv('SCANSAN_API_KEY')
        if not self.api_key:
            raise ValueError("Scansan API key required. Set SCANSAN_API_KEY in .env")
        
        self.api_key = self.api_key.strip('"').strip("'")
        self.rate_limit_delay = rate_limit_delay
        self._last_request_time = 0.0
        
        self.session = requests.Session()
        self.session.headers.update({
            'X-Auth-Token': self.api_key,
            'Accept': 'application/json'
        })
    
    @staticmethod
    def _format_postcode(postcode: str) -> str:
        """Format postcode for API requests (URL-safe)."""
        clean = ' '.join(postcode.strip().upper().split())
        return quote(clean, safe='')
    
    def _rate_limit(self):
        """Enforce rate limiting between requests."""
        elapsed = time.time() - self._last_request_time
        if elapsed < self.rate_limit_delay:
            time.sleep(self.rate_limit_delay - elapsed)
    
    def _request(self, endpoint: str, params: Dict = None, retries: int = 3) -> Dict:
        """
        Make API request with rate limiting and retry logic.
        
        Args:
            endpoint: API endpoint path
            params: Optional query parameters
            retries: Number of retries on rate limit (default 3)
            
        Returns:
            Dict with success status, data/error, and source
        """
        self._rate_limit()
        
        try:
            url = f"{self.BASE_URL}/{endpoint}"
            response = self.session.get(url, params=params, timeout=30)
            self._last_request_time = time.time()
            
            if response.status_code == 200:
                try:
                    return {"success": True, "data": response.json(), "source": "scansan"}
                except json.JSONDecodeError:
                    return {"success": True, "data": response.text, "source": "scansan"}
            elif response.status_code == 429:
                if retries > 0:
                    wait_time = self.rate_limit_delay * (4 - retries) * 2
                    time.sleep(wait_time)
                    return self._request(endpoint, params, retries - 1)
                return {"success": False, "error": "Rate limited - try again later", "source": "scansan"}
            elif response.status_code == 401:
                return {"success": False, "error": "Authentication failed - check API key", "source": "scansan"}
            elif response.status_code == 404:
                return {"success": False, "error": f"Not found: {endpoint}", "source": "scansan"}
            elif response.status_code == 400:
                return {"success": False, "error": "Bad request - check parameters", "source": "scansan"}
            else:
                return {"success": False, "error": f"HTTP {response.status_code}", "source": "scansan"}
        except requests.exceptions.Timeout:
            return {"success": False, "error": "Request timeout", "source": "scansan"}
        except requests.exceptions.ConnectionError:
            return {"success": False, "error": "Connection error", "source": "scansan"}
        except Exception as e:
            return {"success": False, "error": str(e), "source": "scansan"}
    
    # =========================================================================
    # AREA CODE ENDPOINTS
    # =========================================================================
    
    def search_area_codes(self, query: str = None) -> Dict:
        """
        Search for area codes.
        
        Endpoint: GET /area_codes/search
        """
        params = {"q": query} if query else None
        return self._request("area_codes/search", params)
    
    def get_area_summary(self, postcode: str) -> Dict:
        """
        Get summary data for an area/postcode.
        
        Endpoint: GET /area_codes/{postcode}/summary
        """
        return self._request(f"area_codes/{self._format_postcode(postcode)}/summary")
    
    def get_rent_listings(self, postcode: str) -> Dict:
        """
        Get rental listings for an area.
        
        Endpoint: GET /area_codes/{postcode}/rent/listings
        """
        return self._request(f"area_codes/{self._format_postcode(postcode)}/rent/listings")
    
    def get_sale_listings(self, postcode: str) -> Dict:
        """
        Get properties for sale in an area.
        
        Endpoint: GET /area_codes/{postcode}/sale/listings
        """
        return self._request(f"area_codes/{self._format_postcode(postcode)}/sale/listings")
    
    def get_crime_summary(self, postcode: str) -> Dict:
        """
        Get crime summary for an area.
        
        Endpoint: GET /area_codes/{postcode}/crime/summary
        """
        return self._request(f"area_codes/{self._format_postcode(postcode)}/crime/summary")
    
    def get_crime_detail(self, postcode: str) -> Dict:
        """
        Get detailed crime data for an area.
        
        Endpoint: GET /area_codes/{postcode}/crime/detail
        """
        return self._request(f"area_codes/{self._format_postcode(postcode)}/crime/detail")
    
    # =========================================================================
    # POSTCODE ENDPOINTS
    # =========================================================================
    
    def get_sale_history(self, postcode: str) -> Dict:
        """
        Get sale history for a postcode.
        
        Endpoint: GET /postcode/{postcode}/sale/history
        """
        return self._request(f"postcode/{self._format_postcode(postcode)}/sale/history")
    
    def get_classification(self, postcode: str) -> Dict:
        """
        Get postcode classification.
        
        Endpoint: GET /postcode/{postcode}/classification
        """
        return self._request(f"postcode/{self._format_postcode(postcode)}/classification")
    
    def get_addresses(self, postcode: str) -> Dict:
        """
        Get all addresses in a postcode.
        
        Endpoint: GET /postcode/{postcode}/addresses
        """
        return self._request(f"postcode/{self._format_postcode(postcode)}/addresses")
    
    def get_regeneration(self, postcode: str) -> Dict:
        """
        Get regeneration data for an area.
        
        Endpoint: GET /postcode/{postcode}/regeneration
        """
        return self._request(f"postcode/{self._format_postcode(postcode)}/regeneration")
    
    def get_current_valuations(self, postcode: str) -> Dict:
        """
        Get current property valuations.
        
        Endpoint: GET /postcode/{postcode}/valuations/current
        """
        return self._request(f"postcode/{self._format_postcode(postcode)}/valuations/current")
    
    def get_historical_valuations(self, postcode: str) -> Dict:
        """
        Get historical property valuations.
        
        Endpoint: GET /postcode/{postcode}/valuations/historical
        """
        return self._request(f"postcode/{self._format_postcode(postcode)}/valuations/historical")
    
    def get_energy_performance(self, postcode: str) -> Dict:
        """
        Get EPC data for a postcode.
        
        Endpoint: GET /postcode/{postcode}/energy/performance
        """
        return self._request(f"postcode/{self._format_postcode(postcode)}/energy/performance")
    
    def get_census_data(self, postcode: str) -> Dict:
        """
        Get census data for a postcode.
        
        Endpoint: GET /postcode/{postcode}/census
        """
        return self._request(f"postcode/{self._format_postcode(postcode)}/census")
    
    def get_amenities(self, postcode: str) -> Dict:
        """
        Get local amenities for a postcode.
        
        Endpoint: GET /postcode/{postcode}/amenities
        """
        return self._request(f"postcode/{self._format_postcode(postcode)}/amenities")
    
    def get_lha_rates(self, postcode: str) -> Dict:
        """
        Get Local Housing Allowance rates.
        
        Endpoint: GET /postcode/{postcode}/lha
        """
        return self._request(f"postcode/{self._format_postcode(postcode)}/lha")
    
    # =========================================================================
    # DISTRICT ENDPOINTS
    # =========================================================================
    
    def get_district_growth(self, district: str) -> Dict:
        """
        Get price growth data for a district.
        
        Endpoint: GET /district/{district}/growth
        """
        return self._request(f"district/{self._format_postcode(district)}/growth")
    
    def get_rent_demand(self, district: str) -> Dict:
        """
        Get rental demand data for a district.
        
        Endpoint: GET /district/{district}/rent/demand
        """
        return self._request(f"district/{self._format_postcode(district)}/rent/demand")
    
    def get_sale_demand(self, district: str) -> Dict:
        """
        Get sales demand data for a district.
        
        Endpoint: GET /district/{district}/sale/demand
        """
        return self._request(f"district/{self._format_postcode(district)}/sale/demand")
    
    # =========================================================================
    # PROPERTY ENDPOINTS
    # =========================================================================
    
    def get_property_planning(self, property_id: str) -> Dict:
        """
        Get planning permission data for a property.
        
        Endpoint: GET /property/{property_id}/planning_permission
        """
        return self._request(f"property/{property_id}/planning_permission")
    
    def get_property_addresses(self, property_id: str) -> Dict:
        """
        Get address history for a property.
        
        Endpoint: GET /property/{property_id}/addresses
        """
        return self._request(f"property/{property_id}/addresses")
    
    def get_property_energy(self, property_id: str) -> Dict:
        """
        Get energy performance data for a property.
        
        Endpoint: GET /property/{property_id}/energy/performance
        """
        return self._request(f"property/{property_id}/energy/performance")
    
    # =========================================================================
    # CONVENIENCE METHODS
    # =========================================================================
    
    def get_full_postcode_report(self, postcode: str) -> Dict:
        """Get comprehensive data for a postcode."""
        report = {"postcode": postcode, "source": "scansan", "data": {}}
        
        endpoints = [
            ("summary", self.get_area_summary),
            ("sale_history", self.get_sale_history),
            ("current_valuations", self.get_current_valuations),
            ("classification", self.get_classification),
            ("crime_summary", self.get_crime_summary),
            ("amenities", self.get_amenities),
            ("census", self.get_census_data),
            ("lha_rates", self.get_lha_rates),
        ]
        
        for name, func in endpoints:
            try:
                result = func(postcode)
                report["data"][name] = result.get("data") if result.get("success") else {"error": result.get("error")}
            except Exception as e:
                report["data"][name] = {"error": str(e)}
        
        report["success"] = any("error" not in v for v in report["data"].values() if isinstance(v, dict))
        return report
    
    def get_full_district_report(self, district: str) -> Dict:
        """Get comprehensive data for a district."""
        report = {"district": district, "source": "scansan", "data": {}}
        
        endpoints = [
            ("growth", self.get_district_growth),
            ("rent_demand", self.get_rent_demand),
            ("sale_demand", self.get_sale_demand),
        ]
        
        for name, func in endpoints:
            try:
                result = func(district)
                report["data"][name] = result.get("data") if result.get("success") else {"error": result.get("error")}
            except Exception as e:
                report["data"][name] = {"error": str(e)}
        
        report["success"] = any("error" not in v for v in report["data"].values() if isinstance(v, dict))
        return report
    
    def get_full_property_report(self, property_id: str) -> Dict:
        """Get comprehensive data for a property."""
        report = {"property_id": property_id, "source": "scansan", "data": {}}
        
        endpoints = [
            ("planning", self.get_property_planning),
            ("addresses", self.get_property_addresses),
            ("energy", self.get_property_energy),
        ]
        
        for name, func in endpoints:
            try:
                result = func(property_id)
                report["data"][name] = result.get("data") if result.get("success") else {"error": result.get("error")}
            except Exception as e:
                report["data"][name] = {"error": str(e)}
        
        report["success"] = any("error" not in v for v in report["data"].values() if isinstance(v, dict))
        return report


def search_scansan(postcode: str, endpoint: str = "summary") -> Dict:
    """Convenience function to query Scansan API."""
    api = ScansanAPI()
    
    endpoint_map = {
        "summary": api.get_area_summary,
        "sale_listings": api.get_sale_listings,
        "rent_listings": api.get_rent_listings,
        "sale_history": api.get_sale_history,
        "valuations": api.get_current_valuations,
        "historical_valuations": api.get_historical_valuations,
        "crime": api.get_crime_summary,
        "crime_detail": api.get_crime_detail,
        "amenities": api.get_amenities,
        "census": api.get_census_data,
        "classification": api.get_classification,
        "addresses": api.get_addresses,
        "lha": api.get_lha_rates,
        "energy": api.get_energy_performance,
        "regeneration": api.get_regeneration,
    }
    
    if endpoint not in endpoint_map:
        return {"success": False, "error": f"Unknown endpoint: {endpoint}", "source": "scansan"}
    
    return endpoint_map[endpoint](postcode)


if __name__ == "__main__":
    import sys
    
    print("=" * 70)
    print("  Scansan Property Data API Client - Full Test")
    print("=" * 70)
    
    try:
        api = ScansanAPI()
        print("API client initialized\n")
    except ValueError as e:
        print(f"Error: {e}")
        sys.exit(1)
    
    test_postcode = sys.argv[1] if len(sys.argv) > 1 else "NW1 0BH"
    test_district = test_postcode.split()[0] if " " in test_postcode else test_postcode[:3]
    test_property_id = "34019560"
    
    print(f"Test Postcode: {test_postcode}")
    print(f"Test District: {test_district}")
    print(f"Test Property ID: {test_property_id}")
    print("-" * 70)
    
    # Test Area Code Endpoints
    print("\n[AREA CODE ENDPOINTS]")
    tests = [
        ("Area Code Search", lambda: api.search_area_codes()),
        ("Area Summary", lambda: api.get_area_summary(test_postcode)),
        ("Rent Listings", lambda: api.get_rent_listings(test_postcode)),
        ("Sale Listings", lambda: api.get_sale_listings(test_postcode)),
        ("Crime Summary", lambda: api.get_crime_summary(test_postcode)),
        ("Crime Detail", lambda: api.get_crime_detail(test_postcode)),
    ]
    
    for name, func in tests:
        result = func()
        status = "OK" if result.get("success") else "FAIL"
        if result.get("success"):
            data = result.get("data", {})
            if isinstance(data, dict):
                print(f"  [{status}] {name}: {len(data)} fields")
            elif isinstance(data, list):
                print(f"  [{status}] {name}: {len(data)} items")
            else:
                print(f"  [{status}] {name}")
        else:
            print(f"  [{status}] {name}: {result.get('error', 'Unknown')[:40]}")
    
    # Test Postcode Endpoints
    print("\n[POSTCODE ENDPOINTS]")
    tests = [
        ("Sale History", lambda: api.get_sale_history(test_postcode)),
        ("Classification", lambda: api.get_classification(test_postcode)),
        ("Addresses", lambda: api.get_addresses(test_postcode)),
        ("Regeneration", lambda: api.get_regeneration(test_postcode)),
        ("Current Valuations", lambda: api.get_current_valuations(test_postcode)),
        ("Historical Valuations", lambda: api.get_historical_valuations(test_postcode)),
        ("Energy Performance", lambda: api.get_energy_performance(test_postcode)),
        ("Census Data", lambda: api.get_census_data(test_postcode)),
        ("Amenities", lambda: api.get_amenities(test_postcode)),
        ("LHA Rates", lambda: api.get_lha_rates(test_postcode)),
    ]
    
    for name, func in tests:
        result = func()
        status = "OK" if result.get("success") else "FAIL"
        if result.get("success"):
            data = result.get("data", {})
            if isinstance(data, dict):
                print(f"  [{status}] {name}: {len(data)} fields")
            elif isinstance(data, list):
                print(f"  [{status}] {name}: {len(data)} items")
            else:
                print(f"  [{status}] {name}")
        else:
            print(f"  [{status}] {name}: {result.get('error', 'Unknown')[:40]}")
    
    # Test District Endpoints
    print("\n[DISTRICT ENDPOINTS]")
    tests = [
        ("District Growth", lambda: api.get_district_growth(test_district)),
        ("Rent Demand", lambda: api.get_rent_demand(test_district)),
        ("Sale Demand", lambda: api.get_sale_demand(test_district)),
    ]
    
    for name, func in tests:
        result = func()
        status = "OK" if result.get("success") else "FAIL"
        if result.get("success"):
            data = result.get("data", {})
            if isinstance(data, dict):
                print(f"  [{status}] {name}: {len(data)} fields")
            elif isinstance(data, list):
                print(f"  [{status}] {name}: {len(data)} items")
            else:
                print(f"  [{status}] {name}")
        else:
            print(f"  [{status}] {name}: {result.get('error', 'Unknown')[:40]}")
    
    # Test Property Endpoints
    print("\n[PROPERTY ENDPOINTS]")
    tests = [
        ("Property Planning", lambda: api.get_property_planning(test_property_id)),
        ("Property Addresses", lambda: api.get_property_addresses(test_property_id)),
        ("Property Energy", lambda: api.get_property_energy(test_property_id)),
    ]
    
    for name, func in tests:
        result = func()
        status = "OK" if result.get("success") else "FAIL"
        if result.get("success"):
            data = result.get("data", {})
            if isinstance(data, dict):
                print(f"  [{status}] {name}: {len(data)} fields")
            elif isinstance(data, list):
                print(f"  [{status}] {name}: {len(data)} items")
            else:
                print(f"  [{status}] {name}")
        else:
            print(f"  [{status}] {name}: {result.get('error', 'Unknown')[:40]}")
    
    print("\n" + "=" * 70)
    print("Test complete!")
