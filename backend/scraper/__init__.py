"""
Multi-Source Property Scraper Module

A comprehensive Python module for scraping UK residential and commercial property data.
Supports multiple reliable sources:
- Land Registry (Official UK Government Data)

Uses official APIs and Playwright to return structured JSON data.
"""

from .land_registry_scraper import LandRegistryScraper, search_land_registry
from .multi_source_scraper import MultiSourcePropertyScraper, search_property_multi_source

__all__ = [
    'LandRegistryScraper',
    'search_land_registry',
    'MultiSourcePropertyScraper',
    'search_property_multi_source'
]

__version__ = '2.1.0'
