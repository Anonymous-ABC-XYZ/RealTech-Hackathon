"""
Environment Agency Flood Risk Scraper (Open Data)
Source: https://environment.data.gov.uk/flood-monitoring/doc/reference

Fetches real-time and long-term flood risk data for a given location.
"""

import requests
import logging
from typing import Dict, Optional, List

logger = logging.getLogger(__name__)

class FloodRiskScraper:
    """
    Client for Environment Agency Flood Monitoring API.
    Provides flood alerts, warnings, and risk proximity.
    """
    
    BASE_URL = "https://environment.data.gov.uk/flood-monitoring/id"
    
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            "Accept": "application/json",
            "User-Agent": "PropertyResilienceModel/1.0"
        })

    def get_flood_risk(self, lat: float, lng: float, radius_km: float = 1.0) -> Dict:
        """
        Check for flood alerts or warnings within a radius of a coordinate.
        
        Args:
            lat: Latitude
            lng: Longitude
            radius_km: Search radius in kilometers (default 1.0km)
            
        Returns:
            Dict containing risk level and nearest alert details.
        """
        try:
            # Query for active floods/alerts
            # The API allows filtering by lat/long and dist (in km)
            endpoint = f"{self.BASE_URL}/floods"
            params = {
                "lat": lat,
                "long": lng,
                "dist": radius_km
            }
            
            response = self.session.get(endpoint, params=params, timeout=10)
            
            if response.status_code != 200:
                logger.warning(f"Flood API returned {response.status_code}")
                return self._default_low_risk()
                
            data = response.json()
            items = data.get("items", [])
            
            if not items:
                return self._default_low_risk()
            
            # Analyze alerts to determine risk level
            highest_severity = 4 # 1=Severe, 2=Warning, 3=Alert, 4=None
            nearest_alert = None
            
            for item in items:
                severity = item.get("severityLevel", 4)
                if severity < highest_severity:
                    highest_severity = severity
                    nearest_alert = item
            
            # Map severity to risk score (Higher score = Higher Risk)
            # Severity 1 (Severe) -> High (10)
            # Severity 2 (Warning) -> Medium-High (7)
            # Severity 3 (Alert) -> Medium (4)
            # Severity 4 (None) -> Low (0)
            
            risk_map = {
                1: {"level": "High", "score": 10},
                2: {"level": "Medium-High", "score": 7},
                3: {"level": "Medium", "score": 4},
                4: {"level": "Low", "score": 0}
            }
            
            risk_info = risk_map.get(highest_severity, risk_map[4])
            
            return {
                "success": True,
                "risk_level": risk_info["level"],
                "risk_score": risk_info["score"],
                "flood_source": "Environment Agency",
                "active_alerts": len(items),
                "nearest_alert_message": nearest_alert.get("message") if nearest_alert else None,
                "coordinates": {"lat": lat, "lng": lng}
            }

        except Exception as e:
            logger.error(f"Error fetching flood risk: {str(e)}")
            return {
                "success": False,
                "error": str(e),
                "risk_level": "Unknown",
                "risk_score": 0, # Default to 0 on error to not break model
                "flood_source": "Environment Agency"
            }

    def _default_low_risk(self) -> Dict:
        return {
            "success": True,
            "risk_level": "Low",
            "risk_score": 0,
            "flood_source": "Environment Agency",
            "active_alerts": 0
        }

def get_flood_risk(lat: float, lng: float) -> Dict:
    """Convenience function for flood risk."""
    scraper = FloodRiskScraper()
    return scraper.get_flood_risk(lat, lng)

if __name__ == "__main__":
    # Test with a known flood-prone area (East Lyng, Somerset)
    print("Testing East Lyng (Flood Prone):")
    print(get_flood_risk(51.0559, -2.9517))
    
    print("\nTesting London (Generic):")
    print(get_flood_risk(51.5074, -0.1278))
