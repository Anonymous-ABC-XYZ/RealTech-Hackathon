import tls_client
from bs4 import BeautifulSoup
import json
import re
from typing import Dict, List, Optional
from urllib.parse import quote_plus
from .advanced_tls_client import create_stealth_session


class OnTheMarketScraper:
    """
    Scraper for OnTheMarket UK property data.
    Uses advanced anti-detection.
    """
    
    def __init__(self):
        # Use advanced stealth client
        self.client = create_stealth_session()
        self.base_url = "https://www.onthemarket.com"
    
    def search_property(self, address: str) -> Dict:
        """
        Search for property data on OnTheMarket.
        
        Args:
            address: Full UK property address or postcode
            
        Returns:
            Dict containing property data
        """
        try:
            # Visit homepage first
            self.client.visit_homepage_first(self.base_url)
            
            # Search for properties
            search_url = f"{self.base_url}/for-sale/property/{quote_plus(address)}/"
            response = self.client.get(search_url, referer=self.base_url)
            
            if response.status_code == 200:
                soup = BeautifulSoup(response.text, 'lxml')
                property_data = self._extract_property_data(soup, address)
                property_data["success"] = True
                property_data["source"] = "OnTheMarket"
                return property_data
            else:
                return {
                    "success": False,
                    "error": f"Search failed with status {response.status_code}",
                    "source": "OnTheMarket",
                    "address": address
                }
                
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "source": "OnTheMarket",
                "address": address
            }
    
    def _extract_property_data(self, soup: BeautifulSoup, address: str) -> Dict:
        """Extract property data from OnTheMarket listing page."""
        data = {
            "current_listing": None,
            "current_price": None,
            "bedrooms": None,
            "bathrooms": None,
            "property_type": None,
            "tenure": None,
            "listing_url": None,
            "agent": None,
            "features": [],
            "added_on": None
        }
        
        # Find property cards
        property_cards = soup.find_all('li', class_=re.compile(r'property-result', re.I))
        if not property_cards:
            property_cards = soup.find_all('div', class_=re.compile(r'property.*card', re.I))
        
        if property_cards:
            first_card = property_cards[0]
            
            # Extract price
            price_elem = first_card.find('span', class_=re.compile(r'price', re.I))
            if not price_elem:
                price_elem = first_card.find('a', class_=re.compile(r'price', re.I))
            if price_elem:
                data["current_listing"] = True
                data["current_price"] = price_elem.get_text(strip=True)
            
            # Extract property details
            title_elem = first_card.find('h2')
            if not title_elem:
                title_elem = first_card.find('a', class_=re.compile(r'title', re.I))
            if title_elem:
                title_text = title_elem.get_text(strip=True)
                data["property_type"] = title_text
                
                # Extract bedrooms
                bed_match = re.search(r'(\d+)\s+bed', title_text.lower())
                if bed_match:
                    data["bedrooms"] = int(bed_match.group(1))
                
                # Extract bathrooms
                bath_match = re.search(r'(\d+)\s+bath', title_text.lower())
                if bath_match:
                    data["bathrooms"] = int(bath_match.group(1))
            
            # Extract listing URL
            link_elem = first_card.find('a', href=re.compile(r'/details/'))
            if link_elem and 'href' in link_elem.attrs:
                listing_url = link_elem['href']
                if not listing_url.startswith('http'):
                    listing_url = self.base_url + listing_url
                data["listing_url"] = listing_url
                
                # Get detailed info
                detailed_data = self._get_property_details(listing_url)
                data.update(detailed_data)
            
            # Extract agent name
            agent_elem = first_card.find('span', class_=re.compile(r'agent', re.I))
            if agent_elem:
                data["agent"] = agent_elem.get_text(strip=True)
        
        return data
    
    def _get_property_details(self, url: str) -> Dict:
        """Get detailed property information from listing page."""
        details = {}
        
        try:
            # Human-like delay
            self.client.simulate_mouse_movement()
            
            response = self.client.get(url, referer=self.base_url)
            if response.status_code != 200:
                return details
            
            soup = BeautifulSoup(response.text, 'lxml')
            
            # Extract tenure
            details_section = soup.find('dl', class_=re.compile(r'property.*details', re.I))
            if details_section:
                dt_elements = details_section.find_all('dt')
                dd_elements = details_section.find_all('dd')
                
                for dt, dd in zip(dt_elements, dd_elements):
                    dt_text = dt.get_text(strip=True).lower()
                    dd_text = dd.get_text(strip=True)
                    
                    if 'tenure' in dt_text:
                        if 'freehold' in dd_text.lower():
                            details["tenure"] = "Freehold"
                        elif 'leasehold' in dd_text.lower():
                            details["tenure"] = "Leasehold"
                        else:
                            details["tenure"] = dd_text
                    elif 'added' in dt_text or 'listed' in dt_text:
                        details["added_on"] = dd_text
                    elif 'type' in dt_text and not details.get("property_type"):
                        details["property_type"] = dd_text
            
            # Extract agent
            agent_elem = soup.find('div', class_=re.compile(r'agent.*details', re.I))
            if agent_elem:
                agent_name = agent_elem.find('h2')
                if not agent_name:
                    agent_name = agent_elem.find('a')
                if agent_name:
                    details["agent"] = agent_name.get_text(strip=True)
            
            # Extract features
            features_section = soup.find('ul', class_=re.compile(r'features', re.I))
            if features_section:
                feature_items = features_section.find_all('li')
                details["features"] = [f.get_text(strip=True) for f in feature_items]
            
            # Extract description
            desc_elem = soup.find('div', class_=re.compile(r'description', re.I))
            if not desc_elem:
                desc_elem = soup.find('section', id=re.compile(r'description', re.I))
            if desc_elem:
                # Remove script tags
                for script in desc_elem.find_all('script'):
                    script.decompose()
                details["description"] = desc_elem.get_text(strip=True)[:500]
            
            # Extract floorplan URL if available
            floorplan = soup.find('img', class_=re.compile(r'floorplan', re.I))
            if floorplan and 'src' in floorplan.attrs:
                details["floorplan_url"] = floorplan['src']
            
        except Exception as e:
            details["detail_error"] = str(e)
        
        return details


def search_onthemarket(address: str) -> Dict:
    """
    Convenience function to search OnTheMarket.
    
    Args:
        address: UK property address or postcode
        
    Returns:
        Dictionary with property information from OnTheMarket
    """
    scraper = OnTheMarketScraper()
    return scraper.search_property(address)
