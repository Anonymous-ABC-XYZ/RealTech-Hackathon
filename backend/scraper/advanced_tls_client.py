"""
Advanced TLS Client with Maximum Anti-Detection
Mimics real browser behavior to bypass bot protection
"""

import tls_client
import random
import time
from typing import Dict, Optional
from fake_useragent import UserAgent


class AdvancedTLSClient:
    """
    TLS client configured to appear as a real human browser.
    Implements multiple anti-detection techniques.
    """
    
    def __init__(self):
        # Rotate between different browser profiles
        self.browser_profiles = [
            "chrome_120",
            "chrome_119", 
            "chrome_118",
            "safari_ios_16_5",
            "safari_15_6_1",
            "firefox_117",
            "firefox_120"
        ]
        
        # Initialize with random profile
        profile = random.choice(self.browser_profiles)
        
        self.session = tls_client.Session(
            client_identifier=profile,
            random_tls_extension_order=True
        )
        
        # Initialize fake user agent generator
        self.ua = UserAgent(browsers=['chrome', 'firefox', 'safari', 'edge'])
        
        # Track cookies for session persistence
        self.cookies = {}
        
    def get_realistic_headers(self, url: str, referer: Optional[str] = None) -> Dict:
        """
        Generate realistic browser headers that mimic human behavior.
        """
        # Parse domain from URL
        from urllib.parse import urlparse
        parsed = urlparse(url)
        domain = parsed.netloc
        
        # Generate realistic user agent
        user_agent = self.ua.random
        
        # Comprehensive headers that match real browsers
        headers = {
            'User-Agent': user_agent,
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
            'Accept-Language': 'en-GB,en-US;q=0.9,en;q=0.8',
            'Accept-Encoding': 'gzip, deflate, br',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
            'Sec-Fetch-Dest': 'document',
            'Sec-Fetch-Mode': 'navigate',
            'Sec-Fetch-Site': 'none' if not referer else 'same-origin',
            'Sec-Fetch-User': '?1',
            'Cache-Control': 'max-age=0',
            'DNT': '1',
            'sec-ch-ua': '"Not_A Brand";v="8", "Chromium";v="120", "Google Chrome";v="120"',
            'sec-ch-ua-mobile': '?0',
            'sec-ch-ua-platform': '"macOS"',
        }
        
        # Add referer if provided
        if referer:
            headers['Referer'] = referer
        else:
            # Sometimes first visit shouldn't have referer
            pass
        
        # Add domain-specific headers for common sites
        if 'rightmove' in domain.lower():
            headers['sec-ch-ua-platform'] = '"Windows"'
        elif 'zoopla' in domain.lower():
            headers['sec-ch-ua-platform'] = '"macOS"'
        
        return headers
    
    def human_delay(self, min_seconds: float = 1.0, max_seconds: float = 3.0):
        """
        Add random delay to mimic human browsing behavior.
        """
        delay = random.uniform(min_seconds, max_seconds)
        time.sleep(delay)
    
    def get(self, url: str, headers: Optional[Dict] = None, referer: Optional[str] = None, 
            human_like: bool = True):
        """
        Make GET request with anti-detection measures.
        
        Args:
            url: Target URL
            headers: Custom headers (will be merged with realistic defaults)
            referer: Referer URL
            human_like: Whether to add human-like delays
        """
        # Generate realistic headers
        final_headers = self.get_realistic_headers(url, referer)
        
        # Merge custom headers if provided
        if headers:
            final_headers.update(headers)
        
        # Add human-like delay before request
        if human_like:
            self.human_delay(0.5, 2.0)
        
        # Make request
        response = self.session.get(url, headers=final_headers)
        
        # Store cookies for session persistence
        if response.cookies:
            self.cookies.update(response.cookies)
        
        return response
    
    def post(self, url: str, data: Dict = None, headers: Optional[Dict] = None, 
             referer: Optional[str] = None, human_like: bool = True):
        """
        Make POST request with anti-detection measures.
        """
        # Generate realistic headers
        final_headers = self.get_realistic_headers(url, referer)
        final_headers['Content-Type'] = 'application/x-www-form-urlencoded'
        
        # Merge custom headers
        if headers:
            final_headers.update(headers)
        
        # Add human-like delay
        if human_like:
            self.human_delay(0.8, 2.5)
        
        # Make request
        response = self.session.post(url, data=data, headers=final_headers)
        
        # Store cookies
        if response.cookies:
            self.cookies.update(response.cookies)
        
        return response
    
    def visit_homepage_first(self, base_url: str):
        """
        Visit homepage before making actual request to establish session.
        Real users typically visit homepage before searching.
        """
        try:
            # Visit homepage with realistic headers
            self.get(base_url, human_like=True)
            
            # Additional human-like delay
            self.human_delay(1.0, 3.0)
            
            return True
        except:
            return False
    
    def simulate_mouse_movement(self):
        """
        Simulate time that would be spent with mouse movements/reading.
        """
        self.human_delay(2.0, 5.0)
    
    def get_session_cookies(self):
        """
        Get current session cookies.
        """
        return self.cookies
    
    def rotate_identity(self):
        """
        Rotate browser identity for next request.
        Useful for multiple requests to avoid fingerprinting.
        """
        profile = random.choice(self.browser_profiles)
        self.session = tls_client.Session(
            client_identifier=profile,
            random_tls_extension_order=True
        )
        
        # Clear cookies when rotating identity
        self.cookies = {}


def create_stealth_session():
    """
    Factory function to create a stealth TLS session.
    """
    return AdvancedTLSClient()
