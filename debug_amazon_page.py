#!/usr/bin/env python3

import sys
import os
from playwright.sync_api import sync_playwright
from bs4 import BeautifulSoup

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def debug_amazon_page():
    """Debug what Amazon page actually returns"""
    
    print("🔍 Debugging Amazon Page Content")
    print("=" * 50)
    
    url = "https://www.amazon.in/s?k=iphone"
    
    try:
        with sync_playwright() as p:
            browser = p.chromium.launch(
                headless=False,  # Set to False to see the browser
                args=["--no-sandbox", "--disable-blink-features=AutomationControlled"]
            )

            context = browser.new_context(
                user_agent=(
                    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                    "AppleWebKit/537.36 (KHTML, like Gecko) "
                    "Chrome/124.0.0.0 Safari/537.36"
                ),
                locale="en-IN",
                timezone_id="Asia/Kolkata",
                viewport={"width": 1920, "height": 1080}
            )

            context.add_init_script(
                "Object.defineProperty(navigator, 'webdriver', { get: () => undefined });"
            )

            page = context.new_page()

            print(f"🌐 Navigating to: {url}")
            
            # Try different wait strategies
            try:
                page.goto(url, wait_until="networkidle", timeout=30000)
                print("✅ Page loaded with networkidle")
            except Exception as e:
                print(f"⚠️  Networkidle failed: {e}")
                try:
                    page.goto(url, wait_until="domcontentloaded", timeout=30000)
                    print("✅ Page loaded with domcontentloaded")
                except Exception as e2:
                    print(f"❌ Both loading strategies failed: {e2}")
                    return

            # Wait and check page content
            page.wait_for_timeout(5000)
            
            # Check if we're on a captcha or blocked page
            title = page.title()
            print(f"📄 Page title: {title}")
            
            # Check for common Amazon elements
            checks = [
                ("Search input", "input[type='text']"),
                ("Logo", "#nav-logo"),
                ("Search results", "div[data-component-type='s-search-result']"),
                ("Alternative results", "div.s-result-item"),
                ("Any product cards", "[data-asin]"),
                ("Captcha", "form[action*='captcha']"),
                ("Robot check", ".a-box-group"),
                ("Error page", ".error-page")
            ]
            
            print("\n🔍 Page element checks:")
            for name, selector in checks:
                elements = page.query_selector_all(selector)
                count = len(elements)
                status = "✅" if count > 0 else "❌"
                print(f"  {status} {name}: {count} found")
                
                if name == "Search results" and count > 0:
                    print(f"    First result HTML preview:")
                    first_element = elements[0]
                    html_preview = first_element.inner_html()[:200]
                    print(f"    {html_preview}...")
            
            # Get page HTML and analyze
            html = page.content()
            soup = BeautifulSoup(html, "html.parser")
            
            print(f"\n📊 HTML Analysis:")
            print(f"  Total HTML length: {len(html)} characters")
            print(f"  Body text length: {len(soup.get_text())} characters")
            
            # Look for any product-related content
            product_indicators = [
                "data-asin",
                "s-result-item", 
                "a-price",
                "s-price",
                "product",
                "iphone"
            ]
            
            print(f"\n🔍 Product content indicators:")
            for indicator in product_indicators:
                count = len(soup.select(f"[{indicator}]")) if indicator.startswith('data-') else len(soup.select(f".{indicator}"))
                text_count = html.lower().count(indicator)
                print(f"  {indicator}: {count} elements, {text_count} text occurrences")
            
            # Save HTML for manual inspection
            with open("amazon_debug.html", "w", encoding="utf-8") as f:
                f.write(html)
            print(f"\n💾 HTML saved to 'amazon_debug.html' for manual inspection")
            
            # Wait for user input before closing (if not headless)
            if not browser.contexts[0].browser._is_connected:
                input("Press Enter to close browser...")
            
            browser.close()

    except Exception as e:
        print(f"❌ Debug failed: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    debug_amazon_page()
