import tls_client
from bs4 import BeautifulSoup
import json
import re
from typing import Dict, Optional, List
from urllib.parse import quote_plus
from .advanced_tls_client import create_stealth_session


class RightmoveScraper:
    """
    Scraper for UK residential and commercial property data from Rightmove.
    Uses advanced TLS client with anti-detection to bypass bot protection.
    """
    
    def __init__(self):
        # Use advanced stealth client
        self.client = create_stealth_session()
        self.base_url = "https://www.rightmove.co.uk"
    
    def search_property_by_address(self, address: str) -> Dict:
        """
        Search for a property by address and return comprehensive data.
        
        Args:
            address: Full UK property address
            
        Returns:
            Dict containing property data including current price, last sale info, tenure, etc.
        """
        try:
            # Step 1: Visit homepage first to establish session (mimic human behavior)
            self.client.visit_homepage_first(self.base_url)
            
            # Step 2: Search for the property
            search_url = f"{self.base_url}/property-for-sale/search.html?searchLocation={quote_plus(address)}"
            response = self.client.get(search_url, referer=self.base_url)
            
            if response.status_code != 200:
                return {
                    "success": False,
                    "error": f"Search failed with status code {response.status_code}",
                    "address": address
                }
            
            soup = BeautifulSoup(response.text, 'lxml')
            
            # Try to find property listing
            property_data = self._extract_property_data(soup, address)
            
            # If not currently for sale, search sold prices
            if not property_data.get("current_listing"):
                sold_data = self._search_sold_prices(address)
                property_data.update(sold_data)
            
            property_data["success"] = True
            property_data["address"] = address
            
            return property_data
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "address": address
            }
    
    def _extract_property_data(self, soup: BeautifulSoup, address: str) -> Dict:
        """Extract property data from search results page."""
        data = {
            "current_listing": None,
            "current_price": None,
            "price_qualifier": None,
            "bedrooms": None,
            "property_type": None,
            "tenure": None,
            "added_on": None,
            "listing_url": None,
            "agent": None,
            "features": []
        }
        
        # Find first property card
        property_card = soup.find('div', class_=re.compile(r'propertyCard'))
        
        if not property_card:
            return data
        
        # Extract current price
        price_elem = property_card.find('span', class_=re.compile(r'propertyCard-priceValue'))
        if price_elem:
            data["current_listing"] = True
            data["current_price"] = price_elem.text.strip()
        
        # Extract property type and bedrooms
        title_elem = property_card.find('h2', class_=re.compile(r'propertyCard-title'))
        if title_elem:
            title_text = title_elem.text.strip()
            data["property_type"] = title_text
            
            # Extract bedroom count
            bed_match = re.search(r'(\d+)\s+bed', title_text.lower())
            if bed_match:
                data["bedrooms"] = int(bed_match.group(1))
        
        # Extract property link for detailed data
        link_elem = property_card.find('a', class_=re.compile(r'propertyCard-link'))
        if link_elem and 'href' in link_elem.attrs:
            property_url = link_elem['href']
            if not property_url.startswith('http'):
                property_url = self.base_url + property_url
            data["listing_url"] = property_url
            
            # Get detailed property data
            detailed_data = self._get_property_details(property_url)
            data.update(detailed_data)
        
        return data
    
    def _get_property_details(self, url: str) -> Dict:
        """Get detailed property information from property page."""
        details = {}
        
        try:
            # Simulate human delay before visiting detail page
            self.client.simulate_mouse_movement()
            
            response = self.client.get(url, referer=self.base_url)
            if response.status_code != 200:
                return details
            
            soup = BeautifulSoup(response.text, 'lxml')
            
            # Extract tenure (freehold/leasehold)
            tenure_elem = soup.find(string=re.compile(r'Tenure', re.IGNORECASE))
            if tenure_elem:
                parent = tenure_elem.find_parent()
                if parent:
                    tenure_text = parent.get_text()
                    if 'freehold' in tenure_text.lower():
                        details["tenure"] = "Freehold"
                    elif 'leasehold' in tenure_text.lower():
                        details["tenure"] = "Leasehold"
                    else:
                        details["tenure"] = tenure_text.strip()
            
            # Extract added date
            added_elem = soup.find(string=re.compile(r'Added on', re.IGNORECASE))
            if added_elem:
                added_text = added_elem.strip()
                date_match = re.search(r'Added on (.+)', added_text)
                if date_match:
                    details["added_on"] = date_match.group(1).strip()
            
            # Extract agent info
            agent_elem = soup.find('a', class_=re.compile(r'agent.*name', re.IGNORECASE))
            if not agent_elem:
                agent_elem = soup.find(string=re.compile(r'Marketed by', re.IGNORECASE))
                if agent_elem:
                    agent_parent = agent_elem.find_parent()
                    if agent_parent:
                        details["agent"] = agent_parent.get_text().replace('Marketed by', '').strip()
            else:
                details["agent"] = agent_elem.text.strip()
            
            # Extract key features
            features_list = soup.find_all('li', class_=re.compile(r'key.*feature', re.IGNORECASE))
            if features_list:
                details["features"] = [feat.text.strip() for feat in features_list]
            
            # Extract property description
            desc_elem = soup.find('div', class_=re.compile(r'description', re.IGNORECASE))
            if desc_elem:
                details["description"] = desc_elem.get_text(strip=True)[:500]
            
        except Exception as e:
            details["detail_error"] = str(e)
        
        return details
    
    def _search_sold_prices(self, address: str) -> Dict:
        """Search for sold price history."""
        sold_data = {
            "last_sale_price": None,
            "last_sale_date": None,
            "sale_history": []
        }
        
        try:
            # Search sold prices with human-like delay
            sold_url = f"{self.base_url}/house-prices/search.html?searchLocation={quote_plus(address)}"
            response = self.client.get(sold_url, referer=self.base_url)
            
            if response.status_code != 200:
                return sold_data
            
            soup = BeautifulSoup(response.text, 'lxml')
            
            # Find sold price cards
            sold_cards = soup.find_all('div', class_=re.compile(r'soldPrice', re.IGNORECASE))
            
            for card in sold_cards:
                price_elem = card.find('div', class_=re.compile(r'price', re.IGNORECASE))
                date_elem = card.find('div', class_=re.compile(r'date', re.IGNORECASE))
                
                if price_elem and date_elem:
                    sale_info = {
                        "price": price_elem.text.strip(),
                        "date": date_elem.text.strip()
                    }
                    sold_data["sale_history"].append(sale_info)
            
            # Get most recent sale
            if sold_data["sale_history"]:
                sold_data["last_sale_price"] = sold_data["sale_history"][0]["price"]
                sold_data["last_sale_date"] = sold_data["sale_history"][0]["date"]
        
        except Exception as e:
            sold_data["sold_error"] = str(e)
        
        return sold_data
    
    def get_property_data(self, address: str) -> str:
        """
        Main method to get property data in JSON format.
        
        Args:
            address: UK property address
            
        Returns:
            JSON string with property data
        """
        data = self.search_property_by_address(address)
        return json.dumps(data, indent=2)


def scrape_property(address: str) -> Dict:
    """
    Convenience function to scrape property data.
    
    Args:
        address: UK property address
        
    Returns:
        Dictionary with property information
    """
    scraper = RightmoveScraper()
    return scraper.search_property_by_address(address)
