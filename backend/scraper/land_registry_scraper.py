import tls_client
import json
import re
from typing import Dict, List, Optional
from datetime import datetime


class LandRegistryScraper:
    """
    Scraper for UK Land Registry Price Paid Data (Official Government Source).
    This is the most reliable source for historical UK property sale prices.
    """
    
    def __init__(self):
        self.session = tls_client.Session(
            client_identifier="chrome_120",
            random_tls_extension_order=True
        )
        self.base_url = "https://landregistry.data.gov.uk"
        self.api_url = "https://landregistry.data.gov.uk/data/ppi/transaction-record"
        
    def search_by_postcode(self, postcode: str) -> Dict:
        """
        Search Land Registry for property transactions by postcode.
        This is official government data and is free to access.
        
        Args:
            postcode: UK postcode (e.g., "SW1A 2AA")
            
        Returns:
            Dict with property sale history
        """
        try:
            postcode_clean = postcode.upper().replace(" ", "%20")
            
            # Land Registry SPARQL query
            query = f"""
            PREFIX  xsd:  <http://www.w3.org/2001/XMLSchema#>
            PREFIX  text: <http://jena.apache.org/text#>
            PREFIX  ppd:  <http://landregistry.data.gov.uk/def/ppi/>
            PREFIX  lrcommon: <http://landregistry.data.gov.uk/def/common/>
            
            SELECT  ?addr ?postcode ?amount ?date ?category
            WHERE
              {{ ?transx ppd:pricePaid ?amount ;
                        ppd:transactionDate ?date ;
                        ppd:transactionCategory/skos:prefLabel ?category ;
                        ppd:propertyAddress ?addr .
                ?addr lrcommon:postcode "{postcode_clean}"^^xsd:string .
                ?addr lrcommon:postcode ?postcode
              }}
            ORDER BY DESC(?date)
            LIMIT 100
            """
            
            headers = {
                'Accept': 'application/json',
                'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36'
            }
            
            response = self.session.get(
                f"{self.base_url}/landregistry/query",
                params={'query': query},
                headers=headers
            )
            
            if response.status_code == 200:
                data = response.json()
                return self._parse_land_registry_response(data, postcode)
            else:
                # Fallback: Try the REST API
                return self._search_by_postcode_rest(postcode)
                
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "source": "Land Registry",
                "postcode": postcode
            }
    
    def _search_by_postcode_rest(self, postcode: str) -> Dict:
        """Fallback method using Land Registry REST API."""
        try:
            # Use the simpler Price Paid Data API
            url = f"http://landregistry.data.gov.uk/data/ppi/postcode/{postcode.replace(' ', '')}.json"
            
            headers = {
                'Accept': 'application/json',
                'User-Agent': 'Mozilla/5.0'
            }
            
            response = self.session.get(url, headers=headers)
            
            if response.status_code == 200:
                data = response.json()
                return self._parse_land_registry_response(data, postcode)
            else:
                return {
                    "success": False,
                    "error": f"Land Registry returned status {response.status_code}",
                    "source": "Land Registry",
                    "postcode": postcode
                }
                
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "source": "Land Registry",
                "postcode": postcode
            }
    
    def _parse_land_registry_response(self, data: Dict, postcode: str) -> Dict:
        """Parse Land Registry API response."""
        try:
            results = data.get('result', {}).get('items', [])
            
            if not results:
                results = data.get('items', [])
            
            sales = []
            for item in results:
                sale = {
                    "price": item.get('pricePaid', item.get('amount', {}).get('value')),
                    "date": item.get('transactionDate', item.get('date', {}).get('value')),
                    "property_type": item.get('propertyType', {}).get('label', 'Unknown'),
                    "tenure": item.get('estateType', {}).get('label', 'Unknown'),
                    "new_build": item.get('newBuild', False),
                    "address": self._format_address(item.get('propertyAddress', {}))
                }
                sales.append(sale)
            
            if sales:
                return {
                    "success": True,
                    "source": "Land Registry (Official Gov Data)",
                    "postcode": postcode,
                    "last_sale_price": sales[0]['price'],
                    "last_sale_date": sales[0]['date'],
                    "sale_history": sales[:20],  # Last 20 sales
                    "total_transactions": len(sales)
                }
            else:
                return {
                    "success": False,
                    "error": "No transactions found for this postcode",
                    "source": "Land Registry",
                    "postcode": postcode
                }
                
        except Exception as e:
            return {
                "success": False,
                "error": f"Parse error: {str(e)}",
                "source": "Land Registry",
                "postcode": postcode
            }
    
    def _format_address(self, addr_obj: Dict) -> str:
        """Format address object into string."""
        parts = []
        if isinstance(addr_obj, dict):
            for key in ['paon', 'saon', 'street', 'town', 'postcode']:
                val = addr_obj.get(key, {})
                if isinstance(val, dict):
                    val = val.get('label', val.get('value', ''))
                if val:
                    parts.append(str(val))
        return ", ".join(parts) if parts else "Address not available"


def search_land_registry(postcode: str) -> Dict:
    """
    Convenience function to search Land Registry.
    
    Args:
        postcode: UK postcode
        
    Returns:
        Dictionary with sale history from official government data
    """
    scraper = LandRegistryScraper()
    return scraper.search_by_postcode(postcode)
