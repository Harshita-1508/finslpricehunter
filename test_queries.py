#!/usr/bin/env python3

import requests
import time
import re

def test_search_queries():
    """Test different search queries to verify functionality"""
    
    base_url = "http://127.0.0.1:5000"
    test_queries = ['iphone', 'laptop', 'headphones', 'macbook', 'samsung']
    
    print("🔍 Testing Search Queries")
    print("=" * 50)
    
    for query in test_queries:
        try:
            response = requests.post(f"{base_url}/search", data={'query': query})
            
            if response.status_code == 200:
                # Count products using regex
                match = re.search(r'(\d+) products found', response.text)
                if match:
                    count = match.group(1)
                    print(f'✅ "{query}": {count} products found')
                    
                    # Check if data is passed to JavaScript
                    if 'backendProducts = []' in response.text:
                        print(f'   ⚠️  Warning: Empty backend data')
                    elif 'backendProducts = [' in response.text:
                        # Count products in JavaScript
                        js_match = re.search(r'backendProducts = (\[[^\]]*\])', response.text)
                        if js_match:
                            products_str = js_match.group(1)
                            js_count = products_str.count('{')
                            print(f'   📊 JavaScript received {js_count} products')
                    
                else:
                    print(f'❓ "{query}": Could not count products')
            else:
                print(f'❌ "{query}": HTTP {response.status_code}')
                
        except Exception as e:
            print(f'❌ "{query}": Error - {e}')
        
        time.sleep(0.5)  # Small delay between requests
    
    print("\n🎯 Test Complete!")

if __name__ == "__main__":
    test_search_queries()
