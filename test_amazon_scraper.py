#!/usr/bin/env python3

import sys
import os

# Add the project root to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from backend.scrapers.amazon import AmazonScraper
from backend.config import MAX_RESULTS_PER_PLATFORM

def test_amazon_scraper():
    """Test Amazon scraper with improved implementation"""
    
    print("🧪 Testing Amazon Scraper Improvements")
    print("=" * 50)
    
    scraper = AmazonScraper()
    test_queries = ['iphone', 'laptop', 'headphones', 'watch', 'speaker']
    
    for query in test_queries:
        print(f"\n🔍 Testing query: '{query}'")
        print("-" * 30)
        
        try:
            results = scraper.search(query)
            
            print(f"📊 Results count: {len(results)}")
            
            if len(results) == 0:
                print("❌ No results found!")
                continue
                
            # Check if we have the minimum required results
            if len(results) >= 5:
                print("✅ Minimum 5 products found")
            else:
                print(f"⚠️  Only {len(results)} products found (need at least 5)")
                
            # Check if we have reasonable number of results
            if len(results) >= 10:
                print("✅ Good: 10+ products found")
            elif len(results) >= 5:
                print("✅ Acceptable: 5-9 products found")
            else:
                print(f"❌ Poor: Only {len(results)} products found")
            
            # Validate product data
            valid_products = 0
            for i, product in enumerate(results[:3]):  # Check first 3 products
                print(f"\n  📦 Product {i+1}:")
                print(f"     Name: {product.name[:50]}...")
                print(f"     Platform: {product.platform}")
                print(f"     Price: ₹{product.current_price}")
                print(f"     Rating: {product.rating}")
                print(f"     URL: {product.listing_url[:50]}...")
                
                # Validate required fields
                if product.name and len(product.name) >= 5:
                    valid_products += 1
                if product.current_price and product.current_price > 0:
                    valid_products += 0.5
                if product.listing_url:
                    valid_products += 0.5
                    
            print(f"\n  📈 Data quality score: {valid_products}/5.0")
            
        except Exception as e:
            print(f"❌ Error testing '{query}': {e}")
            import traceback
            traceback.print_exc()
    
    print(f"\n🎯 Amazon Scraper Test Complete!")
    print(f"📋 Expected: 5-10 products per query")
    print(f"📋 MAX_RESULTS_PER_PLATFORM: {MAX_RESULTS_PER_PLATFORM}")

if __name__ == "__main__":
    test_amazon_scraper()
