#!/usr/bin/env python3

import sys
import os
sys.path.append(os.path.dirname(__file__))

from services.comparator import PriceComparator

def test_search():
    print("🔍 Testing search functionality...")
    
    comparator = PriceComparator()
    
    # Test with a simple query
    query = "iphone"
    print(f"Searching for: {query}")
    
    try:
        results = comparator.search_all(query)
        print(f"Found {len(results)} results")
        
        if results:
            print("\n📱 First 3 results:")
            for i, result in enumerate(results[:3]):
                print(f"{i+1}. {result.name[:60]}...")
                print(f"   Platform: {result.platform}")
                print(f"   Price: ₹{result.current_price}")
                print(f"   URL: {result.listing_url[:80]}...")
                print()
        else:
            print("❌ No results found")
            
    except Exception as e:
        print(f"❌ Error during search: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_search()
