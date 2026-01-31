"""
Multi-Source Property Scraper Module

A comprehensive Python module for scraping UK residential and commercial property data.
Supports multiple reliable sources:
- Land Registry (Official UK Government Data)
- Zoopla
- OnTheMarket
- Rightmove

Uses tls-client to bypass bot detection and returns structured JSON data.
"""

from .rightmove_scraper import RightmoveScraper, scrape_property
from .zoopla_scraper import ZooplaScraper, search_zoopla
from .onthemarket_scraper import OnTheMarketScraper, search_onthemarket
from .land_registry_scraper import LandRegistryScraper, search_land_registry
from .multi_source_scraper import MultiSourcePropertyScraper, search_property_multi_source

__all__ = [
    'RightmoveScraper',
    'scrape_property',
    'ZooplaScraper',
    'search_zoopla',
    'OnTheMarketScraper',
    'search_onthemarket',
    'LandRegistryScraper',
    'search_land_registry',
    'MultiSourcePropertyScraper',
    'search_property_multi_source'
]

__version__ = '2.0.0'
