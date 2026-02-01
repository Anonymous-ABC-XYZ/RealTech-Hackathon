"""
Multi-Source Property Data Scraper
Aggregates data from multiple reliable UK property sources.
"""

from typing import Dict, List, Optional
import asyncio
from concurrent.futures import ThreadPoolExecutor
import json
import requests

from .land_registry_scraper import search_land_registry
from .flood_risk_scraper import get_flood_risk


class MultiSourcePropertyScraper:
    """
    Aggregates property data from multiple sources for maximum reliability.
    Sources: Land Registry (Gov), Environment Agency (Flood)
    """
    
    def __init__(self):
        self.sources = {
            'land_registry': search_land_registry
        }
    
    def _get_coords_from_postcode(self, postcode: str) -> Optional[Dict[str, float]]:
        """Get coordinates from postcode using free postcodes.io API"""
        try:
            response = requests.get(f"https://api.postcodes.io/postcodes/{postcode}", timeout=5)
            if response.status_code == 200:
                data = response.json()
                return {
                    "lat": data["result"]["latitude"],
                    "lng": data["result"]["longitude"]
                }
        except Exception:
            pass
        return None

    def search_all_sources(self, address: str, postcode: str = None) -> Dict:
        """
        Search all sources and aggregate results.
        
        Args:
            address: Full UK property address
            postcode: Optional postcode (required for Land Registry/Flood)
            
        Returns:
            Aggregated property data from all successful sources
        """
        results = {}
        coords = None
        
        # Get coordinates if postcode is available
        if postcode:
            coords = self._get_coords_from_postcode(postcode)
        
        # Use ThreadPoolExecutor for parallel scraping
        with ThreadPoolExecutor(max_workers=4) as executor:
            futures = {}
            
            # Submit all scraping tasks
            if postcode:
                futures['land_registry'] = executor.submit(search_land_registry, postcode)
            
            if coords:
                futures['flood_risk'] = executor.submit(get_flood_risk, coords['lat'], coords['lng'])
            
            # Collect results
            for source, future in futures.items():
                try:
                    result = future.result(timeout=30)
                    results[source] = result
                except Exception as e:
                    results[source] = {
                        "success": False,
                        "error": str(e),
                        "source": source
                    }
        
        # Aggregate the data
        return self._aggregate_results(results, address)
    
    def search_priority_sources(self, address: str, postcode: str = None) -> Dict:
        """
        Search sources in priority order, return first successful result.
        Priority: Land Registry
        """
        # Try Land Registry first (most reliable - official gov data)
        if postcode:
            result = search_land_registry(postcode)
            if result.get("success"):
                return result
        
        # All failed
        return {
            "success": False,
            "error": "All sources failed to return data",
            "address": address
        }
    
    def _aggregate_results(self, results: Dict, address: str) -> Dict:
        """
        Aggregate data from multiple sources into a single response.
        Prioritizes official sources and cross-validates data.
        """
        aggregated = {
            "success": False,
            "address": address,
            "sources_queried": list(results.keys()),
            "successful_sources": [],
            "failed_sources": [],
            "data": {}
        }
        
        # Separate successful and failed sources
        successful = {}
        for source, result in results.items():
            if result.get("success"):
                successful[source] = result
                aggregated["successful_sources"].append(source)
            else:
                aggregated["failed_sources"].append({
                    "source": source,
                    "error": result.get("error", "Unknown error")
                })
        
        if not successful:
            aggregated["error"] = "All sources failed"
            return aggregated
        
        aggregated["success"] = True
        
        # Aggregate last sale data (prefer Land Registry - official data)
        if 'land_registry' in successful:
            lr_data = successful['land_registry']
            aggregated["data"]["last_sale_price"] = lr_data.get("last_sale_price")
            aggregated["data"]["last_sale_date"] = lr_data.get("last_sale_date")
            aggregated["data"]["sale_history"] = lr_data.get("sale_history", [])
            aggregated["data"]["sale_history_source"] = "Land Registry (Official)"
            
        # Aggregate flood risk data
        if 'flood_risk' in successful:
            flood_data = successful['flood_risk']
            aggregated["data"]["flood_risk"] = {
                "risk_level": flood_data.get("risk_level"),
                "risk_score": flood_data.get("risk_score"),
                "active_alerts": flood_data.get("active_alerts"),
                "nearest_alert": flood_data.get("nearest_alert_message")
            }
        
        # Include all raw source data for transparency
        aggregated["raw_sources"] = successful
        
        return aggregated
    
    def _most_common(self, items: List) -> any:
        """Return most common item in list, or first if all unique."""
        if not items:
            return None
        
        # Count occurrences
        from collections import Counter
        counter = Counter(items)
        most_common = counter.most_common(1)
        return most_common[0][0] if most_common else items[0]


def search_property_multi_source(address: str, postcode: str = None, 
                                  strategy: str = "all") -> Dict:
    """
    Search for property data across multiple sources.
    
    Args:
        address: Full UK property address
        postcode: Optional postcode (recommended for Land Registry)
        strategy: "all" (parallel search all) or "priority" (sequential priority)
        
    Returns:
        Dictionary with aggregated property data
    """
    scraper = MultiSourcePropertyScraper()
    
    if strategy == "priority":
        return scraper.search_priority_sources(address, postcode)
    else:
        return scraper.search_all_sources(address, postcode)
