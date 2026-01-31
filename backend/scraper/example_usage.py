"""
Example usage of the Rightmove Property Scraper
"""
from rightmove_scraper import RightmoveScraper, scrape_property
import json


def example_basic_usage():
    """Basic example using the convenience function."""
    print("=" * 60)
    print("EXAMPLE 1: Basic Usage")
    print("=" * 60)
    
    address = "10 Downing Street, London SW1A 2AA"
    data = scrape_property(address)
    
    print(json.dumps(data, indent=2))


def example_with_class():
    """Example using the RightmoveScraper class directly."""
    print("\n" + "=" * 60)
    print("EXAMPLE 2: Using Class Instance")
    print("=" * 60)
    
    scraper = RightmoveScraper()
    
    # Example addresses
    addresses = [
        "Baker Street, London",
        "Oxford Street, London",
        "Piccadilly Circus, London"
    ]
    
    for address in addresses:
        print(f"\n--- Scraping: {address} ---")
        data = scraper.search_property_by_address(address)
        
        if data.get("success"):
            print(f"✓ Success!")
            print(f"  Current Price: {data.get('current_price', 'N/A')}")
            print(f"  Property Type: {data.get('property_type', 'N/A')}")
            print(f"  Tenure: {data.get('tenure', 'N/A')}")
            print(f"  Last Sale: {data.get('last_sale_price', 'N/A')} on {data.get('last_sale_date', 'N/A')}")
        else:
            print(f"✗ Failed: {data.get('error')}")


def example_json_output():
    """Example showing how to get JSON string output."""
    print("\n" + "=" * 60)
    print("EXAMPLE 3: JSON String Output")
    print("=" * 60)
    
    scraper = RightmoveScraper()
    address = "Westminster, London"
    
    json_output = scraper.get_property_data(address)
    print(json_output)


def example_api_simulation():
    """Simulate how the API would use the scraper."""
    print("\n" + "=" * 60)
    print("EXAMPLE 4: API Simulation")
    print("=" * 60)
    
    # Simulating API request with address header
    request_address = "Kings Cross, London"
    
    print(f"Simulating API request with Address header: {request_address}")
    
    # What the API does internally
    property_data = scrape_property(request_address)
    
    # API response
    if property_data.get("success"):
        response = {
            "status": 200,
            "data": property_data
        }
    else:
        response = {
            "status": 404,
            "data": property_data
        }
    
    print(f"\nAPI Response (Status {response['status']}):")
    print(json.dumps(response['data'], indent=2))


if __name__ == "__main__":
    # Run examples
    try:
        example_basic_usage()
        example_with_class()
        example_json_output()
        example_api_simulation()
        
        print("\n" + "=" * 60)
        print("All examples completed!")
        print("=" * 60)
        
    except Exception as e:
        print(f"\nError running examples: {str(e)}")
        print("Make sure you have installed all dependencies:")
        print("pip install tls-client beautifulsoup4 lxml")
