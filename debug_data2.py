#!/usr/bin/env python3

import sys
import os
sys.path.append(os.path.dirname(__file__))

from services.comparator import PriceComparator
import json

def test_object_structure():
    print("🔍 Testing object structure...")
    
    comparator = PriceComparator()
    
    # Test with a simple query
    query = "iphone"
    print(f"Searching for: {query}")
    
    try:
        results = comparator.search_all(query)
        print(f"Found {len(results)} results")
        
        if results:
            print("\n📊 Checking object structure...")
            
            # Check first result
            first_result = results[0]
            print(f"Type: {type(first_result)}")
            print(f"Dir: {[attr for attr in dir(first_result) if not attr.startswith('_')]}")
            
            # Convert to dict manually
            result_dicts = []
            for result in results:
                result_dict = {
                    'name': result.name,
                    'platform': result.platform,
                    'current_price': result.current_price,
                    'original_price': result.original_price,
                    'listing_url': result.listing_url,
                    'image_url': result.image_url,
                    'brand': result.brand,
                    'in_stock': result.in_stock,
                    'rating': result.rating
                }
                result_dicts.append(result_dict)
            
            # Test JSON serialization
            json_data = json.dumps(result_dicts)
            print(f"JSON length: {len(json_data)}")
            
            # Parse back
            parsed_data = json.loads(json_data)
            print(f"Parsed back: {len(parsed_data)} items")
            
            if parsed_data:
                first_item = parsed_data[0]
                print(f"\nFirst item keys: {list(first_item.keys())}")
                print(f"Name: {first_item.get('name', 'N/A')}")
                print(f"Platform: {first_item.get('platform', 'N/A')}")
                print(f"Price: {first_item.get('current_price', 'N/A')}")
                print(f"URL: {first_item.get('listing_url', 'N/A')}")
                
        else:
            print("❌ No results found")
            
    except Exception as e:
        print(f"❌ Error during test: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_object_structure()
