"""
Playwright-based Zoopla Scraper
Uses real browser to bypass Cloudflare protection
"""

from playwright.sync_api import sync_playwright
from bs4 import BeautifulSoup
import json
import re
from typing import Dict
from urllib.parse import quote_plus
import random
import time


class PlaywrightZooplaScraper:
    """
    Zoopla scraper using Playwright.
    Bypasses Cloudflare by using real browser.
    """
    
    def __init__(self, headless: bool = True):
        self.headless = headless
        self.playwright = None
        self.browser = None
        self.base_url = "https://www.zoopla.co.uk"
    
    def __enter__(self):
        self.playwright = sync_playwright().start()
        self.browser = self.playwright.chromium.launch(
            headless=self.headless,
            args=[
                '--disable-blink-features=AutomationControlled',
                '--disable-dev-shm-usage',
                '--no-sandbox'
            ]
        )
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        if self.browser:
            self.browser.close()
        if self.playwright:
            self.playwright.stop()
    
    def _create_stealth_context(self):
        """Create stealth browser context."""
        context = self.browser.new_context(
            viewport={'width': 1920, 'height': 1080},
            user_agent='Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36',
            locale='en-GB',
            timezone_id='Europe/London'
        )
        
        context.add_init_script("""
            Object.defineProperty(navigator, 'webdriver', {get: () => undefined});
            window.navigator.chrome = {runtime: {}};
        """)
        
        return context
    
    def search_property(self, address: str) -> Dict:
        """Search Zoopla for property data."""
        try:
            context = self._create_stealth_context()
            page = context.new_page()
            
            # Visit homepage
            page.goto(self.base_url, wait_until='networkidle')
            time.sleep(random.uniform(1, 2))
            
            # Search for property
            search_url = f"{self.base_url}/for-sale/property/{quote_plus(address)}/"
            page.goto(search_url, wait_until='networkidle', timeout=30000)
            time.sleep(random.uniform(2, 3))
            
            # Wait for listings or error page
            try:
                page.wait_for_selector('[data-testid="search-result"], .listing-results, .error', timeout=10000)
            except:
                pass
            
            content = page.content()
            soup = BeautifulSoup(content, 'lxml')
            
            # Extract data
            property_data = self._extract_property_data(soup, page, address)
            
            # Get sold prices
            sold_data = self._search_sold_prices(page, address)
            property_data.update(sold_data)
            
            property_data["success"] = True
            property_data["source"] = "Zoopla (Playwright)"
            
            context.close()
            return property_data
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "source": "Zoopla (Playwright)",
                "address": address
            }
    
    def _extract_property_data(self, soup, page, address):
        """Extract property information."""
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
        
        # Find listings
        listings = soup.find_all('div', attrs={'data-testid': 'search-result'})
        if not listings:
            listings = soup.find_all('div', class_=re.compile(r'listing', re.I))
        
        if listings:
            first = listings[0]
            
            # Price
            price = first.find('p', attrs={'data-testid': 'listing-price'})
            if not price:
                price = first.find('span', class_=re.compile(r'price', re.I))
            if price:
                data["current_listing"] = True
                data["current_price"] = price.get_text(strip=True)
            
            # Property type
            title = first.find('h2')
            if not title:
                title = first.find('a', attrs={'data-testid': 'listing-details-link'})
            if title:
                title_text = title.get_text(strip=True)
                data["property_type"] = title_text
                
                bed_match = re.search(r'(\d+)\s+bed', title_text.lower())
                if bed_match:
                    data["bedrooms"] = int(bed_match.group(1))
            
            # Listing URL
            link = first.find('a', attrs={'data-testid': 'listing-details-link'})
            if not link:
                link = first.find('a', href=re.compile(r'/for-sale/details/'))
            if link and 'href' in link.attrs:
                url = link['href']
                if not url.startswith('http'):
                    url = self.base_url + url
                data["listing_url"] = url
                
                # Get details
                details = self._get_details(page, url)
                data.update(details)
        
        return data
    
    def _get_details(self, page, url):
        """Get property details from listing page."""
        details = {}
        
        try:
            time.sleep(random.uniform(1, 2))
            page.goto(url, wait_until='networkidle', timeout=20000)
            time.sleep(random.uniform(1, 2))
            
            content = page.content()
            soup = BeautifulSoup(content, 'lxml')
            
            # Tenure
            info_items = soup.find_all('li', attrs={'data-testid': re.compile(r'info')})
            for item in info_items:
                text = item.get_text(strip=True).lower()
                if 'freehold' in text:
                    details["tenure"] = "Freehold"
                elif 'leasehold' in text:
                    details["tenure"] = "Leasehold"
            
            # Agent
            agent = soup.find('a', attrs={'data-testid': 'agent-name'})
            if agent:
                details["agent"] = agent.get_text(strip=True)
            
            # Features
            features = soup.find('ul', attrs={'data-testid': 'key-features'})
            if features:
                items = features.find_all('li')
                details["features"] = [f.get_text(strip=True) for f in items]
            
        except Exception as e:
            details["detail_error"] = str(e)
        
        return details
    
    def _search_sold_prices(self, page, address):
        """Get sold price history."""
        sold_data = {
            "last_sale_price": None,
            "last_sale_date": None,
            "sale_history": []
        }
        
        try:
            sold_url = f"{self.base_url}/house-prices/{quote_plus(address)}/"
            page.goto(sold_url, wait_until='networkidle', timeout=20000)
            time.sleep(random.uniform(1, 2))
            
            content = page.content()
            soup = BeautifulSoup(content, 'lxml')
            
            sold_listings = soup.find_all('div', class_=re.compile(r'sold.*price', re.I))
            if not sold_listings:
                sold_listings = soup.find_all('article', class_=re.compile(r'transaction', re.I))
            
            for listing in sold_listings[:10]:
                price = listing.find('span', class_=re.compile(r'price', re.I))
                date = listing.find('span', class_=re.compile(r'date', re.I))
                
                if price and date:
                    sold_data["sale_history"].append({
                        "price": price.get_text(strip=True),
                        "date": date.get_text(strip=True)
                    })
            
            if sold_data["sale_history"]:
                sold_data["last_sale_price"] = sold_data["sale_history"][0]["price"]
                sold_data["last_sale_date"] = sold_data["sale_history"][0]["date"]
        
        except Exception as e:
            sold_data["sold_error"] = str(e)
        
        return sold_data


def scrape_zoopla_playwright(address: str, headless: bool = True) -> Dict:
    """
    Scrape Zoopla using Playwright.
    
    Args:
        address: UK property address
        headless: Run in headless mode
        
    Returns:
        Property data dictionary
    """
    with PlaywrightZooplaScraper(headless=headless) as scraper:
        return scraper.search_property(address)
