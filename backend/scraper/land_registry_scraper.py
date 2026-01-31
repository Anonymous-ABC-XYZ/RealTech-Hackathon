"""
UK Land Registry Price Paid Data Scraper

This module provides access to official UK property sale data from HM Land Registry's
Price Paid Data (PPD) linked data API.

Usage Examples:
--------------
    from scraper.land_registry_scraper import LandRegistryScraper, search_land_registry
    
    # 1. Search by street (most reliable)
    scraper = LandRegistryScraper()
    result = scraper.search_by_street("ROLAND GARDENS", "LONDON")
    
    # 2. Search by address
    result = scraper.search_by_address("14 Roland Gardens", town="LONDON")
    
    # 3. Use convenience function
    result = search_land_registry("ROLAND GARDENS", town="LONDON")
    
    # 4. Access results
    if result['success']:
        for t in result['transactions']:
            print(f"{t['address']}: £{t['price']:,} on {t['date']}")
        print(f"Average price: £{result['statistics']['average_price']:,}")

Data Returned:
- price: Transaction price in GBP
- date: Date of transaction
- property_type: Detached, Semi-Detached, Terraced, Flat/Maisonette
- tenure: Freehold or Leasehold
- new_build: Whether property was a new build
- Full address components

API Reference:
- Source: HM Land Registry Price Paid Data
- URL: https://landregistry.data.gov.uk/
- Coverage: England and Wales only (from 1995)
"""

import requests
from typing import Dict, List, Optional
from datetime import datetime


class LandRegistryScraper:
    """
    Scraper for UK Land Registry Price Paid Data.
    
    Uses the official HM Land Registry linked data API to retrieve
    property transaction records.
    """
    
    API_BASE = "https://landregistry.data.gov.uk/data/ppi/transaction-record.json"
    
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            "Accept": "application/json",
            "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36"
        })
    
    def search_by_postcode(self, postcode: str, limit: int = 50) -> Dict:
        """
        Search for property transactions by postcode.
        
        Note: Street search often returns better results.
        
        Args:
            postcode: UK postcode (e.g., "SW7 3RP")
            limit: Maximum results (default 50)
            
        Returns:
            Dict with transactions and statistics
        """
        postcode = self._normalize_postcode(postcode)
        return self._query_api({"propertyAddress.postcode": postcode}, limit)
    
    def search_by_street(self, street: str, town: str = None, limit: int = 50) -> Dict:
        """
        Search for property transactions by street name.
        
        This is the most reliable search method.
        
        Args:
            street: Street name (e.g., "ROLAND GARDENS")
            town: Optional town/city (e.g., "LONDON") - recommended
            limit: Maximum results (default 50)
            
        Returns:
            Dict with transactions and statistics
            
        Example:
            >>> scraper = LandRegistryScraper()
            >>> result = scraper.search_by_street("ROLAND GARDENS", "LONDON")
            >>> print(f"Found {len(result['transactions'])} sales")
        """
        params = {"propertyAddress.street": street.upper()}
        if town:
            params["propertyAddress.town"] = town.upper()
        return self._query_api(params, limit)
    
    def search_by_address(self, address: str, town: str = None, postcode: str = None, limit: int = 20) -> Dict:
        """
        Search for a specific property address.
        
        Args:
            address: Address string (e.g., "14 Roland Gardens")
            town: Town/city (e.g., "LONDON") - recommended
            postcode: Optional postcode
            limit: Maximum results
            
        Returns:
            Dict with transactions and statistics
            
        Example:
            >>> scraper = LandRegistryScraper()
            >>> result = scraper.search_by_address("14 Roland Gardens", town="LONDON")
        """
        # Extract house number and street
        parts = address.split(" ", 1)
        if len(parts) == 2 and parts[0].isdigit():
            paon, street = parts[0], parts[1]
        else:
            paon, street = None, address
        
        params = {"propertyAddress.street": street.upper()}
        if paon:
            params["propertyAddress.paon"] = paon
        if town:
            params["propertyAddress.town"] = town.upper()
        if postcode:
            params["propertyAddress.postcode"] = self._normalize_postcode(postcode)
        
        return self._query_api(params, limit)
    
    def _normalize_postcode(self, postcode: str) -> str:
        """Normalize postcode format to include space."""
        postcode = postcode.upper().strip().replace(" ", "")
        if len(postcode) > 4:
            return postcode[:-3] + " " + postcode[-3:]
        return postcode
    
    def _query_api(self, params: Dict, limit: int) -> Dict:
        """Query the Land Registry linked data API."""
        try:
            query_params = {"_pageSize": str(limit)}
            query_params.update(params)
            
            response = self.session.get(self.API_BASE, params=query_params, timeout=30)
            
            if response.status_code == 200:
                data = response.json()
                return self._parse_response(data, params)
            else:
                return {
                    "success": False,
                    "error": f"API returned status {response.status_code}",
                    "source": "land_registry"
                }
        except requests.RequestException as e:
            return {"success": False, "error": f"Network error: {str(e)}", "source": "land_registry"}
        except Exception as e:
            return {"success": False, "error": str(e), "source": "land_registry"}
    
    def _parse_response(self, data: Dict, query_params: Dict) -> Dict:
        """Parse the API response into clean transaction records."""
        transactions = []
        
        items = data.get("result", {}).get("items", [])
        
        for item in items:
            try:
                addr = item.get("propertyAddress", {})
                estate = item.get("estateType", {})
                prop_type = item.get("propertyType", {})
                
                # Extract tenure
                tenure = self._extract_label(estate, "Unknown")
                
                # Extract property type
                ptype = self._extract_label(prop_type, "Unknown")
                
                # Parse date
                raw_date = item.get("transactionDate", "")
                formatted_date = self._parse_date(raw_date)
                
                transaction = {
                    "price": item.get("pricePaid", 0),
                    "date": formatted_date,
                    "date_raw": raw_date,
                    "property_type": ptype,
                    "new_build": item.get("newBuild", False),
                    "tenure": tenure,
                    "paon": addr.get("paon", ""),
                    "saon": addr.get("saon", ""),
                    "street": addr.get("street", ""),
                    "locality": addr.get("locality", ""),
                    "town": addr.get("town", ""),
                    "district": addr.get("district", ""),
                    "county": addr.get("county", ""),
                    "postcode": addr.get("postcode", ""),
                    "address": self._build_address(addr)
                }
                transactions.append(transaction)
            except Exception:
                continue
        
        # Sort by date (most recent first)
        transactions.sort(key=lambda x: self._date_sort_key(x.get("date_raw", "")), reverse=True)
        
        return self._build_response(transactions, query_params)
    
    def _extract_label(self, obj: Dict, default: str = "Unknown") -> str:
        """Extract label from linked data object."""
        if not isinstance(obj, dict):
            return default
        
        # Try getting from label array
        labels = obj.get("label", [])
        if labels and isinstance(labels, list):
            if isinstance(labels[0], dict):
                return labels[0].get("_value", default)
            return str(labels[0])
        
        # Try getting from prefLabel
        pref_labels = obj.get("prefLabel", [])
        if pref_labels and isinstance(pref_labels, list):
            if isinstance(pref_labels[0], dict):
                return pref_labels[0].get("_value", default)
            return str(pref_labels[0])
        
        # Try extracting from _about URL
        about = obj.get("_about", "")
        if about:
            return about.split("/")[-1].replace("-", " ").title()
        
        return default
    
    def _parse_date(self, date_str: str) -> str:
        """Parse various date formats to readable string."""
        if not date_str:
            return ""
        
        # Handle "Thu, 06 Jun 1996" format
        try:
            dt = datetime.strptime(date_str, "%a, %d %b %Y")
            return dt.strftime("%d %B %Y")
        except ValueError:
            pass
        
        # Handle ISO format
        try:
            if "T" in date_str:
                date_str = date_str.split("T")[0]
            dt = datetime.strptime(date_str[:10], "%Y-%m-%d")
            return dt.strftime("%d %B %Y")
        except ValueError:
            pass
        
        return date_str
    
    def _date_sort_key(self, date_str: str) -> str:
        """Create sortable date key."""
        try:
            dt = datetime.strptime(date_str, "%a, %d %b %Y")
            return dt.strftime("%Y-%m-%d")
        except ValueError:
            return "0000-00-00"
    
    def _build_address(self, addr: Dict) -> str:
        """Build full address string from components."""
        parts = []
        for key in ["saon", "paon", "street", "locality", "town", "postcode"]:
            val = addr.get(key)
            if val:
                parts.append(str(val))
        return ", ".join(parts) if parts else "Address not available"
    
    def _build_response(self, transactions: List[Dict], params: Dict) -> Dict:
        """Build the final response with transactions and statistics."""
        if not transactions:
            return {
                "success": False,
                "error": "No transactions found",
                "query": params,
                "source": "land_registry",
                "transactions": [],
                "statistics": {}
            }
        
        prices = [t["price"] for t in transactions if t.get("price")]
        
        statistics = {}
        if prices:
            sorted_prices = sorted(prices)
            statistics = {
                "count": len(prices),
                "average_price": int(sum(prices) / len(prices)),
                "min_price": min(prices),
                "max_price": max(prices),
                "median_price": sorted_prices[len(sorted_prices) // 2],
                "total_value": sum(prices)
            }
        
        return {
            "success": True,
            "source": "land_registry",
            "query": params,
            "transactions": transactions,
            "statistics": statistics
        }


def search_land_registry(query: str, query_type: str = "auto", town: str = None) -> Dict:
    """
    Convenience function to search Land Registry data.
    
    Automatically detects query type or allows manual specification.
    
    Args:
        query: Search query (street name, address, or postcode)
        query_type: "auto", "street", "address", or "postcode"
        town: Optional town name (recommended for better results)
        
    Returns:
        Dictionary containing:
        - success: bool
        - transactions: List of transaction records
        - statistics: Price statistics (count, average, min, max, median)
        
    Examples:
        # Search by street with town
        result = search_land_registry("ROLAND GARDENS", town="LONDON")
        
        # Force address search
        result = search_land_registry("14 Roland Gardens", query_type="address", town="LONDON")
        
        # Print results
        if result['success']:
            print(f"Found {len(result['transactions'])} transactions")
            print(f"Average price: £{result['statistics']['average_price']:,}")
    """
    scraper = LandRegistryScraper()
    query = query.strip()
    
    if query_type == "auto":
        # Check if looks like postcode (e.g., SW7 3RP)
        q = query.upper().replace(" ", "")
        if 5 <= len(q) <= 8 and len(q) >= 3:
            # Check pattern: letters then number then letters at end
            if q[-3].isdigit() and q[-2:].isalpha():
                query_type = "postcode"
            elif query.split() and query.split()[0].isdigit():
                query_type = "address"
            else:
                query_type = "street"
        elif query.split() and query.split()[0].isdigit():
            query_type = "address"
        else:
            query_type = "street"
    
    if query_type == "postcode":
        return scraper.search_by_postcode(query)
    elif query_type == "address":
        return scraper.search_by_address(query, town=town)
    else:
        return scraper.search_by_street(query, town=town)


# CLI testing
if __name__ == "__main__":
    import json
    
    print("=" * 70)
    print("  UK Land Registry Price Paid Data Scraper")
    print("  Source: HM Land Registry (Official Government Data)")
    print("=" * 70)
    
    scraper = LandRegistryScraper()
    
    # Test 1: Street search
    print("\n[TEST 1] Street Search: ROLAND GARDENS, LONDON")
    print("-" * 70)
    result = scraper.search_by_street("ROLAND GARDENS", "LONDON")
    
    if result["success"]:
        stats = result.get("statistics", {})
        print(f"✓ Found {len(result['transactions'])} transactions")
        print(f"\n  📊 Statistics:")
        print(f"     Average Price: £{stats.get('average_price', 0):,}")
        print(f"     Price Range:   £{stats.get('min_price', 0):,} - £{stats.get('max_price', 0):,}")
        print(f"     Median Price:  £{stats.get('median_price', 0):,}")
        print(f"     Total Value:   £{stats.get('total_value', 0):,}")
        
        print(f"\n  🏠 Recent Sales:")
        for t in result["transactions"][:5]:
            print(f"     {t['address']}")
            print(f"        £{t['price']:,} | {t['date']} | {t['property_type']} | {t['tenure']}")
    else:
        print(f"✗ Error: {result.get('error')}")
    
    # Test 2: Address search
    print("\n" + "-" * 70)
    print("[TEST 2] Address Search: 14 Roland Gardens")
    print("-" * 70)
    result = scraper.search_by_address("14 Roland Gardens", town="LONDON")
    
    if result["success"]:
        print(f"✓ Found {len(result['transactions'])} transactions for this address")
        for t in result["transactions"][:3]:
            print(f"     £{t['price']:,} | {t['date']} | {t['tenure']}")
    else:
        print(f"✗ Error: {result.get('error')}")
    
    # Test 3: Convenience function
    print("\n" + "-" * 70)
    print("[TEST 3] Convenience Function: search_land_registry()")
    print("-" * 70)
    result = search_land_registry("BAKER STREET", town="LONDON")
    if result["success"]:
        print(f"✓ Baker Street, London: {len(result['transactions'])} transactions")
        print(f"  Average: £{result['statistics'].get('average_price', 0):,}")
    else:
        print(f"✗ Error: {result.get('error')}")
    
    print("\n" + "=" * 70)
    print("  Tests Complete!")
    print("=" * 70)
