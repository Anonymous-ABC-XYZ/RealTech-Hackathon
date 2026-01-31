import tls_client
from bs4 import BeautifulSoup
import json
import re
from typing import Dict, List, Optional
from urllib.parse import quote_plus
from .advanced_tls_client import create_stealth_session


class ZooplaScraper:
    """
    Scraper for Zoopla UK property data.
    Uses advanced anti-detection techniques.
    """
    
    def __init__(self):
        # Use advanced stealth client
        self.client = create_stealth_session()
        self.base_url = "https://www.zoopla.co.uk"
    
    def search_property(self, address: str) -> Dict:
        """
        Search for property data on Zoopla.
        
        Args:
            address: Full UK property address or postcode
            
        Returns:
            Dict containing property data
        """
        try:
            # Visit homepage first to establish session
            self.client.visit_homepage_first(self.base_url)
            
            # Try for-sale search first
            search_url = f"{self.base_url}/for-sale/property/{quote_plus(address)}/"
            response = self.client.get(search_url, referer=self.base_url)
            
            if response.status_code == 200:
                soup = BeautifulSoup(response.text, 'lxml')
                property_data = self._extract_property_data(soup, address)
                
                # Also get sold prices
                sold_data = self._search_sold_prices(address)
                property_data.update(sold_data)
                
                property_data["success"] = True
                property_data["source"] = "Zoopla"
                return property_data
            else:
                return {
                    "success": False,
                    "error": f"Search failed with status {response.status_code}",
                    "source": "Zoopla",
                    "address": address
                }
                
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "source": "Zoopla",
                "address": address
            }
    
    def _extract_property_data(self, soup: BeautifulSoup, address: str) -> Dict:
        """Extract property data from Zoopla listing page."""
        data = {
            "current_listing": None,
            "current_price": None,
            "bedrooms": None,
            "property_type": None,
            "tenure": None,
            "listing_url": None,
            "agent": None,
            "features": []
        }
        
        # Look for JSON-LD data (Zoopla often includes structured data)
        script_tags = soup.find_all('script', type='application/ld+json')
        for script in script_tags:
            try:
                json_data = json.loads(script.string)
                if isinstance(json_data, dict) and json_data.get('@type') == 'Product':
                    data["current_listing"] = True
                    offers = json_data.get('offers', {})
                    data["current_price"] = offers.get('price')
                    data["property_type"] = json_data.get('name', '')
            except:
                pass
        
        # Find listing cards
        listings = soup.find_all('div', attrs={'data-testid': 'search-result'})
        if not listings:
            listings = soup.find_all('div', class_=re.compile(r'listing', re.I))
        
        if listings:
            first_listing = listings[0]
            
            # Extract price
            price_elem = first_listing.find('p', attrs={'data-testid': 'listing-price'})
            if not price_elem:
                price_elem = first_listing.find('span', class_=re.compile(r'price', re.I))
            if price_elem:
                data["current_listing"] = True
                data["current_price"] = price_elem.get_text(strip=True)
            
            # Extract title/property type
            title_elem = first_listing.find('h2')
            if not title_elem:
                title_elem = first_listing.find('a', attrs={'data-testid': 'listing-details-link'})
            if title_elem:
                title_text = title_elem.get_text(strip=True)
                data["property_type"] = title_text
                
                # Extract bedrooms
                bed_match = re.search(r'(\d+)\s+bed', title_text.lower())
                if bed_match:
                    data["bedrooms"] = int(bed_match.group(1))
            
            # Extract listing URL
            link_elem = first_listing.find('a', attrs={'data-testid': 'listing-details-link'})
            if not link_elem:
                link_elem = first_listing.find('a', href=re.compile(r'/for-sale/details/'))
            if link_elem and 'href' in link_elem.attrs:
                listing_url = link_elem['href']
                if not listing_url.startswith('http'):
                    listing_url = self.base_url + listing_url
                data["listing_url"] = listing_url
                
                # Get detailed info from listing page
                detailed_data = self._get_property_details(listing_url)
                data.update(detailed_data)
        
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
            info_items = soup.find_all('li', attrs={'data-testid': re.compile(r'info')})
            for item in info_items:
                text = item.get_text(strip=True).lower()
                if 'tenure' in text or 'freehold' in text or 'leasehold' in text:
                    if 'freehold' in text:
                        details["tenure"] = "Freehold"
                    elif 'leasehold' in text:
                        details["tenure"] = "Leasehold"
            
            # Extract agent
            agent_elem = soup.find('a', attrs={'data-testid': 'agent-name'})
            if not agent_elem:
                agent_elem = soup.find('p', class_=re.compile(r'agent.*name', re.I))
            if agent_elem:
                details["agent"] = agent_elem.get_text(strip=True)
            
            # Extract features
            features_section = soup.find('ul', attrs={'data-testid': 'key-features'})
            if features_section:
                feature_items = features_section.find_all('li')
                details["features"] = [f.get_text(strip=True) for f in feature_items]
            
            # Extract description
            desc_elem = soup.find('div', attrs={'data-testid': 'description'})
            if not desc_elem:
                desc_elem = soup.find('div', class_=re.compile(r'description', re.I))
            if desc_elem:
                details["description"] = desc_elem.get_text(strip=True)[:500]
            
        except Exception as e:
            details["detail_error"] = str(e)
        
        return details
    
    def _search_sold_prices(self, address: str) -> Dict:
        """Search for sold price history on Zoopla."""
        sold_data = {
            "last_sale_price": None,
            "last_sale_date": None,
            "sale_history": []
        }
        
        try:
            sold_url = f"{self.base_url}/house-prices/{quote_plus(address)}/"
            response = self.client.get(sold_url, referer=self.base_url)
            
            if response.status_code != 200:
                return sold_data
            
            soup = BeautifulSoup(response.text, 'lxml')
            
            # Find sold price listings
            sold_listings = soup.find_all('div', class_=re.compile(r'sold.*price', re.I))
            if not sold_listings:
                sold_listings = soup.find_all('article', class_=re.compile(r'transaction', re.I))
            
            for listing in sold_listings[:10]:  # Get last 10 sales
                price_elem = listing.find('span', class_=re.compile(r'price', re.I))
                date_elem = listing.find('span', class_=re.compile(r'date', re.I))
                
                if price_elem and date_elem:
                    sale = {
                        "price": price_elem.get_text(strip=True),
                        "date": date_elem.get_text(strip=True)
                    }
                    sold_data["sale_history"].append(sale)
            
            # Get most recent sale
            if sold_data["sale_history"]:
                sold_data["last_sale_price"] = sold_data["sale_history"][0]["price"]
                sold_data["last_sale_date"] = sold_data["sale_history"][0]["date"]
        
        except Exception as e:
            sold_data["sold_error"] = str(e)
        
        return sold_data


def search_zoopla(address: str) -> Dict:
    """
    Convenience function to search Zoopla.
    
    Args:
        address: UK property address or postcode
        
    Returns:
        Dictionary with property information from Zoopla
    """
    scraper = ZooplaScraper()
    return scraper.search_property(address)
