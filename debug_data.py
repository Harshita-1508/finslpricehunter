#!/usr/bin/env python3

import sys
import os
sys.path.append(os.path.dirname(__file__))

from services.comparator import PriceComparator
import json

def test_data_serialization():
    print("🔍 Testing data serialization...")
    
    comparator = PriceComparator()
    
    # Test with a simple query
    query = "iphone"
    print(f"Searching for: {query}")
    
    try:
        results = comparator.search_all(query)
        print(f"Found {len(results)} results")
        
        if results:
            print("\n📊 Testing JSON serialization...")
            
            # Convert to JSON like the template does
            json_data = json.dumps(results, default=str)
            print(f"JSON length: {len(json_data)}")
            
            # Parse back to verify
            parsed_data = json.loads(json_data)
            print(f"Parsed back: {len(parsed_data)} items")
            
            # Check first item structure
            if parsed_data:
                first_item = parsed_data[0]
                print(f"\nFirst item keys: {list(first_item.keys())}")
                print(f"Name: {first_item.get('name', 'N/A')}")
                print(f"Platform: {first_item.get('platform', 'N/A')}")
                print(f"Price: {first_item.get('current_price', 'N/A')}")
                print(f"URL: {first_item.get('listing_url', 'N/A')}")
                
                # Check for missing attributes
                required_attrs = ['name', 'platform', 'current_price', 'listing_url']
                missing = [attr for attr in required_attrs if not first_item.get(attr)]
                if missing:
                    print(f"❌ Missing attributes: {missing}")
                else:
                    print("✅ All required attributes present")
            
        else:
            print("❌ No results found")
            
    except Exception as e:
        print(f"❌ Error during test: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_data_serialization()
