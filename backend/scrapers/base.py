import re
from bs4 import BeautifulSoup


class ScrapedProduct:
    def __init__(self, name, platform, listing_url,
                 current_price=None, original_price=None,
                 image_url=None, brand=None, in_stock=True, rating=None):
        self.name = name
        self.platform = platform
        self.listing_url = listing_url
        self.current_price = current_price
        self.original_price = original_price
        self.image_url = image_url
        self.brand = brand
        self.in_stock = in_stock
        self.rating = rating


class BaseScraper:

    def _get(self, url):
        try:
            from playwright.sync_api import sync_playwright

            print("Fetching:", url)

            with sync_playwright() as p:
                browser = p.chromium.launch(
                    headless=True,
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
                )

                context.add_init_script(
                    "Object.defineProperty(navigator, 'webdriver', { get: () => undefined });"
                )

                page = context.new_page()

                # Improved loading with networkidle and longer timeout
                page.goto(url, wait_until="networkidle", timeout=30000)
                
                # Add delay after loading
                page.wait_for_timeout(3000)

                # Multiple scroll actions to load content
                for _ in range(3):
                    page.evaluate("window.scrollBy(0, document.body.scrollHeight)")
                    page.wait_for_timeout(1000)

                html = page.content()
                browser.close()

                return BeautifulSoup(html, "html.parser")

        except Exception as e:
            print("Error:", e)

        return None

    def parse_price(self, text):
        if not text:
            return None
        text = re.sub(r"[^\d]", "", text)
        return int(text) if text else None