"""
Playwright-based Rightmove Scraper
Uses real browser in headless mode to bypass all bot protection
"""

from playwright.sync_api import sync_playwright, Browser, Page
from bs4 import BeautifulSoup
import json
import re
from typing import Dict, Optional
from urllib.parse import quote_plus
import random
import time


class PlaywrightRightmoveScraper:
    """
    Rightmove scraper using Playwright in headless mode.
    Bypasses Cloudflare and all bot protection by using real browser.
    """
    
    def __init__(self, headless: bool = True):
        self.headless = headless
        self.playwright = None
        self.browser = None
        self.base_url = "https://www.rightmove.co.uk"
    
    def __enter__(self):
        self.playwright = sync_playwright().start()
        # Launch browser with stealth settings
        self.browser = self.playwright.chromium.launch(
            headless=self.headless,
            args=[
                '--disable-blink-features=AutomationControlled',
                '--disable-dev-shm-usage',
                '--no-sandbox',
                '--disable-setuid-sandbox',
                '--disable-web-security',
                '--disable-features=IsolateOrigins,site-per-process'
            ]
        )
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        if self.browser:
            self.browser.close()
        if self.playwright:
            self.playwright.stop()
    
    def _create_stealth_context(self):
        """Create browser context with anti-detection."""
        context = self.browser.new_context(
            viewport={'width': 1920, 'height': 1080},
            user_agent='Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            locale='en-GB',
            timezone_id='Europe/London',
            permissions=['geolocation']
        )
        
        # Add stealth scripts
        context.add_init_script("""
            Object.defineProperty(navigator, 'webdriver', {
                get: () => undefined
            });
            
            window.navigator.chrome = {
                runtime: {}
            };
            
            Object.defineProperty(navigator, 'plugins', {
                get: () => [1, 2, 3, 4, 5]
            });
            
            Object.defineProperty(navigator, 'languages', {
                get: () => ['en-GB', 'en-US', 'en']
            });
        """)
        
        return context
    
    def search_property_by_address(self, address: str) -> Dict:
        """
        Search for property using real browser automation.
        
        Args:
            address: Full UK property address
            
        Returns:
            Dict with property data
        """
        try:
            context = self._create_stealth_context()
            page = context.new_page()
            
            # Step 1: Visit homepage (like a real user)
            page.goto(self.base_url, wait_until='networkidle')
            time.sleep(random.uniform(1, 2))
            
            # Step 2: Navigate to search
            search_url = f"{self.base_url}/property-for-sale/search.html?searchLocation={quote_plus(address)}"
            page.goto(search_url, wait_until='networkidle')
            time.sleep(random.uniform(1, 3))
            
            # Get page content
            content = page.content()
            soup = BeautifulSoup(content, 'lxml')
            
            # Extract property data
            property_data = self._extract_property_data(soup, page, address)
            
            # Get sold prices if needed
            if not property_data.get("current_listing"):
                sold_data = self._search_sold_prices(page, address)
                property_data.update(sold_data)
            
            property_data["success"] = True
            property_data["address"] = address
            property_data["source"] = "Rightmove (Playwright)"
            
            context.close()
            return property_data
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "address": address,
                "source": "Rightmove (Playwright)"
            }
    
    def _extract_property_data(self, soup: BeautifulSoup, page: Page, address: str) -> Dict:
        """Extract property data from page."""
        data = {
            "current_listing": None,
            "current_price": None,
            "bedrooms": None,
            "property_type": None,
            "tenure": None,
            "listing_url": None,
            "agent": None,
            "features": [],
            "images": []
        }
        
        # Find property cards
        property_cards = soup.find_all('div', class_=re.compile(r'propertyCard'))
        
        if not property_cards:
            # Try alternative selectors
            property_cards = soup.find_all('div', attrs={'data-test': 'propertyCard'})
        
        if property_cards:
            first_card = property_cards[0]
            
            # Extract price
            price_elem = first_card.find('span', class_=re.compile(r'propertyCard-priceValue'))
            if not price_elem:
                price_elem = first_card.find('div', attrs={'data-test': 'propertyCard-priceValue'})
            if price_elem:
                data["current_listing"] = True
                data["current_price"] = price_elem.get_text(strip=True)
            
            # Extract property type and bedrooms
            title_elem = first_card.find('h2', class_=re.compile(r'propertyCard-title'))
            if not title_elem:
                title_elem = first_card.find('address')
            if title_elem:
                title_text = title_elem.get_text(strip=True)
                data["property_type"] = title_text
                
                bed_match = re.search(r'(\d+)\s+bed', title_text.lower())
                if bed_match:
                    data["bedrooms"] = int(bed_match.group(1))
            
            # Extract listing URL
            link_elem = first_card.find('a', class_=re.compile(r'propertyCard-link'))
            if not link_elem:
                link_elem = first_card.find('a', href=re.compile(r'/properties/'))
            if link_elem and 'href' in link_elem.attrs:
                listing_url = link_elem['href']
                if not listing_url.startswith('http'):
                    listing_url = self.base_url + listing_url
                data["listing_url"] = listing_url
                
                # Visit detail page for more info
                detailed_data = self._get_property_details(page, listing_url)
                data.update(detailed_data)
        
        return data
    
    def _get_property_details(self, page: Page, url: str) -> Dict:
        """Get detailed property info from listing page."""
        details = {}
        
        try:
            time.sleep(random.uniform(1, 2))
            page.goto(url, wait_until='networkidle')
            time.sleep(random.uniform(1, 2))
            
            content = page.content()
            soup = BeautifulSoup(content, 'lxml')
            
            # Extract tenure
            tenure_elem = soup.find(string=re.compile(r'Tenure', re.IGNORECASE))
            if tenure_elem:
                parent = tenure_elem.find_parent()
                if parent:
                    tenure_text = parent.get_text()
                    if 'freehold' in tenure_text.lower():
                        details["tenure"] = "Freehold"
                    elif 'leasehold' in tenure_text.lower():
                        details["tenure"] = "Leasehold"
            
            # Extract key features
            features_list = soup.find_all('li', class_=re.compile(r'key.*feature', re.IGNORECASE))
            if not features_list:
                features_list = soup.find_all('li', attrs={'data-test': re.compile(r'feature')})
            if features_list:
                details["features"] = [f.get_text(strip=True) for f in features_list[:10]]
            
            # Extract agent
            agent_elem = soup.find('a', class_=re.compile(r'agent.*name', re.IGNORECASE))
            if agent_elem:
                details["agent"] = agent_elem.get_text(strip=True)
            
            # Extract description
            desc_elem = soup.find('div', class_=re.compile(r'description', re.IGNORECASE))
            if not desc_elem:
                desc_elem = soup.find('div', attrs={'data-test': 'property-description'})
            if desc_elem:
                details["description"] = desc_elem.get_text(strip=True)[:500]
            
        except Exception as e:
            details["detail_error"] = str(e)
        
        return details
    
    def _search_sold_prices(self, page: Page, address: str) -> Dict:
        """Search sold price history."""
        sold_data = {
            "last_sale_price": None,
            "last_sale_date": None,
            "sale_history": []
        }
        
        try:
            sold_url = f"{self.base_url}/house-prices/search.html?searchLocation={quote_plus(address)}"
            page.goto(sold_url, wait_until='networkidle')
            time.sleep(random.uniform(1, 2))
            
            content = page.content()
            soup = BeautifulSoup(content, 'lxml')
            
            # Find sold transactions
            sold_cards = soup.find_all('div', class_=re.compile(r'soldPrice', re.IGNORECASE))
            
            for card in sold_cards[:10]:
                price_elem = card.find('div', class_=re.compile(r'price', re.IGNORECASE))
                date_elem = card.find('div', class_=re.compile(r'date', re.IGNORECASE))
                
                if price_elem and date_elem:
                    sold_data["sale_history"].append({
                        "price": price_elem.get_text(strip=True),
                        "date": date_elem.get_text(strip=True)
                    })
            
            if sold_data["sale_history"]:
                sold_data["last_sale_price"] = sold_data["sale_history"][0]["price"]
                sold_data["last_sale_date"] = sold_data["sale_history"][0]["date"]
        
        except Exception as e:
            sold_data["sold_error"] = str(e)
        
        return sold_data


def scrape_rightmove_playwright(address: str, headless: bool = True) -> Dict:
    """
    Convenience function to scrape Rightmove using Playwright.
    
    Args:
        address: UK property address
        headless: Run browser in headless mode
        
    Returns:
        Dictionary with property data
    """
    with PlaywrightRightmoveScraper(headless=headless) as scraper:
        return scraper.search_property_by_address(address)
