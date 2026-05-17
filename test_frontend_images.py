#!/usr/bin/env python3

import sys
import os
import requests

# Add the project root to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from services.comparator import PriceComparator

def test_image_urls_directly():
    """Test if the image URLs returned by the scraper are actually accessible"""
    
    print("🌐 Testing Image URLs Directly")
    print("=" * 50)
    
    comparator = PriceComparator()
    
    # Get some results
    results = comparator.search_all("iphone")
    
    amazon_results = [r for r in results if r.platform == "amazon"]
    
    if not amazon_results:
        print("❌ No Amazon results found")
        return
    
    print(f"📦 Testing {len(amazon_results)} Amazon image URLs:")
    
    for i, result in enumerate(amazon_results[:3]):
        image_url = result.image_url
        print(f"\n  📱 Product {i+1}: {result.name[:50]}...")
        print(f"     Image URL: {image_url}")
        
        if not image_url:
            print(f"     ❌ No image URL")
            continue
        
        # Test if the URL is accessible
        try:
            response = requests.head(image_url, timeout=10, allow_redirects=True)
            if response.status_code == 200:
                print(f"     ✅ Image URL accessible (HTTP {response.status_code})")
                
                # Check content type
                content_type = response.headers.get('content-type', '')
                if 'image' in content_type:
                    print(f"     ✅ Content type: {content_type}")
                else:
                    print(f"     ⚠️  Unexpected content type: {content_type}")
            else:
                print(f"     ❌ Image URL not accessible (HTTP {response.status_code})")
        except requests.exceptions.RequestException as e:
            print(f"     ❌ Network error: {e}")
        except Exception as e:
            print(f"     ❌ Error: {e}")

def test_frontend_format():
    """Test if the image URLs are in the correct format for frontend"""
    
    print("\n🎨 Testing Frontend Format")
    print("=" * 50)
    
    comparator = PriceComparator()
    results = comparator.search_all("iphone")
    
    print(f"📊 Checking format for {len(results)} results:")
    
    for i, result in enumerate(results[:5]):
        print(f"\n  📱 Product {i+1} ({result.platform}):")
        print(f"     Name: {result.name[:40]}...")
        print(f"     Image URL: {result.image_url}")
        
        # Check if URL is properly formatted for frontend
        if result.image_url:
            if result.image_url.startswith("http"):
                print(f"     ✅ Valid HTTP URL")
            else:
                print(f"     ⚠️  Invalid URL format")
        else:
            print(f"     ⚠️  Empty image URL")

def test_mock_data_images():
    """Test if mock data has proper image URLs"""
    
    print("\n🧪 Testing Mock Data Images")
    print("=" * 50)
    
    from backend.scrapers.amazon import AmazonScraper
    
    scraper = AmazonScraper()
    
    # Force mock data by triggering the fallback
    results = scraper.search("testquerythatshouldtriggermockdata")
    
    print(f"📦 Mock data returned {len(results)} results:")
    
    for i, result in enumerate(results[:3]):
        print(f"\n  📱 Mock Product {i+1}:")
        print(f"     Name: {result.name[:40]}...")
        print(f"     Image URL: {result.image_url}")
        
        if result.image_url:
            # Test if mock image URL is accessible
            try:
                response = requests.head(result.image_url, timeout=5)
                if response.status_code == 200:
                    print(f"     ✅ Mock image accessible")
                else:
                    print(f"     ❌ Mock image not accessible ({response.status_code})")
            except:
                print(f"     ❌ Mock image network error")

if __name__ == "__main__":
    test_image_urls_directly()
    test_frontend_format()
    test_mock_data_images()
    
    print("\n🎯 Frontend Image Test Complete!")
    print("✅ If image URLs are accessible, the issue is in frontend display")
    print("❌ If image URLs are not accessible, the issue is in URL generation")
