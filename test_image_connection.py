#!/usr/bin/env python3

import sys
import os

# Add the project root to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from services.comparator import PriceComparator

def test_image_extraction_connection():
    """Test if image extraction is properly connected to the search flow"""
    
    print("🔗 Testing Image Extraction Connection")
    print("=" * 50)
    
    comparator = PriceComparator()
    
    # Test with a simple query
    query = "iphone"
    print(f"🔍 Testing search for: {query}")
    
    # This should call the Amazon scraper with our enhanced image extraction
    results = comparator.search_all(query)
    
    print(f"📊 Found {len(results)} total results")
    
    # Check Amazon results specifically
    amazon_results = [r for r in results if r.platform == "amazon"]
    print(f"📦 Amazon results: {len(amazon_results)}")
    
    if amazon_results:
        print("\n🖼️ Checking Amazon image URLs:")
        for i, result in enumerate(amazon_results[:3]):
            print(f"  📱 Product {i+1}: {result.name[:50]}...")
            print(f"     Image URL: {result.image_url}")
            print(f"     Image URL type: {type(result.image_url)}")
            
            if result.image_url:
                if result.image_url.startswith("https://m.media-amazon.com/"):
                    print(f"     ✅ Valid Amazon image URL")
                else:
                    print(f"     ⚠️  Unexpected URL format")
            else:
                print(f"     ❌ No image URL found")
    else:
        print("❌ No Amazon results found")
    
    # Check if we're getting any image URLs at all
    all_image_urls = [r.image_url for r in results if r.image_url]
    print(f"\n📊 Total products with images: {len(all_image_urls)}")
    
    if all_image_urls:
        print("✅ Image extraction is connected and working")
    else:
        print("❌ Image extraction may not be working")
    
    return results

def test_direct_amazon_scraper():
    """Test the Amazon scraper directly to verify image extraction"""
    
    print("\n🎯 Testing Direct Amazon Scraper")
    print("=" * 50)
    
    from backend.scrapers.amazon import AmazonScraper
    
    scraper = AmazonScraper()
    
    # Test direct search
    query = "samsung"
    print(f"🔍 Direct Amazon search for: {query}")
    
    results = scraper.search(query)
    
    print(f"📊 Amazon scraper returned {len(results)} results")
    
    if results:
        print("\n🖼️ Direct image extraction test:")
        for i, result in enumerate(results[:3]):
            print(f"  📱 Product {i+1}: {result.name[:50]}...")
            print(f"     Image URL: {result.image_url}")
            
            if result.image_url:
                print(f"     ✅ Image URL extracted")
            else:
                print(f"     ❌ No image URL")
    else:
        print("❌ No results from Amazon scraper")

if __name__ == "__main__":
    test_image_extraction_connection()
    test_direct_amazon_scraper()
    
    print("\n🎯 Image Connection Test Complete!")
    print("✅ If you see Amazon image URLs above, the connection is working")
    print("❌ If no image URLs, there's a connection issue")
