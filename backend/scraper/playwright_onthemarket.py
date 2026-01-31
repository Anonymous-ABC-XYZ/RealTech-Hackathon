"""
Playwright-based OnTheMarket Scraper
Real browser automation for maximum success rate
"""

from playwright.sync_api import sync_playwright
from bs4 import BeautifulSoup
import re
from typing import Dict
from urllib.parse import quote_plus
import random
import time


class PlaywrightOnTheMarketScraper:
    """OnTheMarket scraper using Playwright."""
    
    def __init__(self, headless: bool = True):
        self.headless = headless
        self.playwright = None
        self.browser = None
        self.base_url = "https://www.onthemarket.com"
    
    def __enter__(self):
        self.playwright = sync_playwright().start()
        self.browser = self.playwright.chromium.launch(
            headless=self.headless,
            args=['--disable-blink-features=AutomationControlled']
        )
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        if self.browser:
            self.browser.close()
        if self.playwright:
            self.playwright.stop()
    
    def _create_context(self):
        """Create browser context."""
        context = self.browser.new_context(
            viewport={'width': 1920, 'height': 1080},
            user_agent='Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36',
            locale='en-GB'
        )
        context.add_init_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined});")
        return context
    
    def search_property(self, address: str) -> Dict:
        """Search OnTheMarket."""
        try:
            context = self._create_context()
            page = context.new_page()
            
            # Visit homepage
            page.goto(self.base_url, wait_until='networkidle')
            time.sleep(random.uniform(1, 2))
            
            # Search
            search_url = f"{self.base_url}/for-sale/property/{quote_plus(address)}/"
            page.goto(search_url, wait_until='networkidle', timeout=30000)
            time.sleep(random.uniform(2, 3))
            
            content = page.content()
            soup = BeautifulSoup(content, 'lxml')
            
            property_data = self._extract_data(soup, page, address)
            property_data["success"] = True
            property_data["source"] = "OnTheMarket (Playwright)"
            
            context.close()
            return property_data
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "source": "OnTheMarket (Playwright)",
                "address": address
            }
    
    def _extract_data(self, soup, page, address):
        """Extract property data."""
        data = {
            "current_listing": None,
            "current_price": None,
            "bedrooms": None,
            "property_type": None,
            "tenure": None,
            "listing_url": None,
            "agent": None,
            "features": [],
            "added_on": None
        }
        
        # Find property cards
        cards = soup.find_all('li', class_=re.compile(r'property-result', re.I))
        if not cards:
            cards = soup.find_all('div', class_=re.compile(r'property.*card', re.I))
        
        if cards:
            first = cards[0]
            
            # Price
            price = first.find('span', class_=re.compile(r'price', re.I))
            if not price:
                price = first.find('a', class_=re.compile(r'price', re.I))
            if price:
                data["current_listing"] = True
                data["current_price"] = price.get_text(strip=True)
            
            # Property details
            title = first.find('h2')
            if not title:
                title = first.find('a', class_=re.compile(r'title', re.I))
            if title:
                text = title.get_text(strip=True)
                data["property_type"] = text
                
                bed_match = re.search(r'(\d+)\s+bed', text.lower())
                if bed_match:
                    data["bedrooms"] = int(bed_match.group(1))
            
            # URL
            link = first.find('a', href=re.compile(r'/details/'))
            if link and 'href' in link.attrs:
                url = link['href']
                if not url.startswith('http'):
                    url = self.base_url + url
                data["listing_url"] = url
                
                details = self._get_details(page, url)
                data.update(details)
            
            # Agent
            agent = first.find('span', class_=re.compile(r'agent', re.I))
            if agent:
                data["agent"] = agent.get_text(strip=True)
        
        return data
    
    def _get_details(self, page, url):
        """Get property details."""
        details = {}
        
        try:
            time.sleep(random.uniform(1, 2))
            page.goto(url, wait_until='networkidle', timeout=20000)
            time.sleep(random.uniform(1, 2))
            
            content = page.content()
            soup = BeautifulSoup(content, 'lxml')
            
            # Tenure
            details_section = soup.find('dl', class_=re.compile(r'property.*details', re.I))
            if details_section:
                dts = details_section.find_all('dt')
                dds = details_section.find_all('dd')
                
                for dt, dd in zip(dts, dds):
                    dt_text = dt.get_text(strip=True).lower()
                    dd_text = dd.get_text(strip=True)
                    
                    if 'tenure' in dt_text:
                        if 'freehold' in dd_text.lower():
                            details["tenure"] = "Freehold"
                        elif 'leasehold' in dd_text.lower():
                            details["tenure"] = "Leasehold"
                    elif 'added' in dt_text:
                        details["added_on"] = dd_text
            
            # Features
            features = soup.find('ul', class_=re.compile(r'features', re.I))
            if features:
                items = features.find_all('li')
                details["features"] = [f.get_text(strip=True) for f in items]
            
        except Exception as e:
            details["detail_error"] = str(e)
        
        return details


def scrape_onthemarket_playwright(address: str, headless: bool = True) -> Dict:
    """Scrape OnTheMarket using Playwright."""
    with PlaywrightOnTheMarketScraper(headless=headless) as scraper:
        return scraper.search_property(address)
