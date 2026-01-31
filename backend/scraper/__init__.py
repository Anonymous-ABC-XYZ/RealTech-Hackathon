"""
Rightmove Property Scraper Module

A Python module for scraping UK residential and commercial property data from Rightmove.
Uses tls-client to bypass bot detection and returns structured JSON data.
"""

from .rightmove_scraper import RightmoveScraper, scrape_property

__all__ = ['RightmoveScraper', 'scrape_property']
__version__ = '1.0.0'
