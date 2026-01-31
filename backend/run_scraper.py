#!/usr/bin/env python3
"""
Run the Land Registry scraper to query UK property transaction data.

Usage:
    python run_scraper.py                              # Run with default test (Roland Gardens)
    python run_scraper.py "BAKER STREET" "LONDON"      # Search street in town
    python run_scraper.py "14 Roland Gardens" address  # Search specific address
    
Examples:
    python run_scraper.py "OXFORD STREET" "LONDON"
    python run_scraper.py "PICCADILLY" "LONDON"
    python run_scraper.py "10 Downing Street" address "LONDON"
"""

import sys
import json

# Import from the scraper module
from scraper.land_registry_scraper import LandRegistryScraper, search_land_registry


def main():
    print("=" * 70)
    print("  RealTech Property Data Scraper - UK Land Registry")
    print("  Source: HM Land Registry Price Paid Data (Official)")
    print("=" * 70)
    
    # Parse command line arguments
    if len(sys.argv) >= 2:
        query = sys.argv[1]
        query_type = "street"
        town = None
        
        if len(sys.argv) >= 3:
            # Check if second arg is query type or town
            if sys.argv[2].lower() in ["street", "address", "postcode"]:
                query_type = sys.argv[2].lower()
                if len(sys.argv) >= 4:
                    town = sys.argv[3]
            else:
                town = sys.argv[2]
    else:
        # Default search
        query = "ROLAND GARDENS"
        town = "LONDON"
        query_type = "street"
    
    print(f"\n🔍 Query: {query}")
    if town:
        print(f"   Town: {town}")
    print(f"   Type: {query_type}")
    print("-" * 70)
    
    # Perform search
    scraper = LandRegistryScraper()
    
    if query_type == "street":
        result = scraper.search_by_street(query, town=town)
    elif query_type == "address":
        result = scraper.search_by_address(query, town=town)
    else:
        result = scraper.search_by_postcode(query)
    
    if result["success"]:
        transactions = result.get("transactions", [])
        stats = result.get("statistics", {})
        
        print(f"\n✅ Found {len(transactions)} property transactions\n")
        
        # Display statistics
        if stats:
            print("📊 Price Statistics:")
            print(f"   Count:         {stats.get('count', 0)}")
            print(f"   Average Price: £{stats.get('average_price', 0):,}")
            print(f"   Min Price:     £{stats.get('min_price', 0):,}")
            print(f"   Max Price:     £{stats.get('max_price', 0):,}")
            print(f"   Median Price:  £{stats.get('median_price', 0):,}")
            print(f"   Total Value:   £{stats.get('total_value', 0):,}")
        
        # Display transactions
        print(f"\n🏠 Recent Transactions:")
        print("-" * 70)
        
        for i, t in enumerate(transactions[:10], 1):
            print(f"\n{i}. {t.get('address', 'Unknown Address')}")
            print(f"   💰 Price:    £{t.get('price', 0):,}")
            print(f"   📅 Date:     {t.get('date', 'Unknown')}")
            print(f"   🏡 Type:     {t.get('property_type', 'Unknown')}")
            print(f"   📜 Tenure:   {t.get('tenure', 'Unknown')}")
            if t.get('new_build'):
                print(f"   🆕 New Build: Yes")
        
        if len(transactions) > 10:
            print(f"\n   ... and {len(transactions) - 10} more transactions")
        
        # Save full results to file
        output_file = "scraper_results.json"
        with open(output_file, "w") as f:
            json.dump(result, f, indent=2)
        print(f"\n💾 Full results saved to: {output_file}")
        
    else:
        print(f"\n❌ Error: {result.get('error', 'Unknown error')}")
        print("\n💡 Tips:")
        print("   - Use street names in UPPERCASE (e.g., 'BAKER STREET')")
        print("   - Include the town name for better results (e.g., 'LONDON')")
        print("   - Try different search types: street, address, postcode")
    
    print("\n" + "=" * 70)


if __name__ == "__main__":
    main()
