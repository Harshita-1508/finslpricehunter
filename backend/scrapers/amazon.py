import re
import json
import os
import time
import random
from typing import Optional
from urllib.parse import urlencode, urljoin
from bs4 import BeautifulSoup

from backend.scrapers.base import BaseScraper, ScrapedProduct
from backend.config import MAX_RESULTS_PER_PLATFORM

AMAZON_BASE = "https://www.amazon.in"
SEARCH_URL = f"{AMAZON_BASE}/s?"
COOKIES_FILE = "amazon_cookies.json"

# ─────────────────────────────────────────────
# CONFIG — fill in whichever backend you prefer
# ─────────────────────────────────────────────
SCRAPER_API_KEY = os.getenv("SCRAPER_API_KEY", "")          # ScraperAPI key (optional)
PROXY_SERVER    = os.getenv("AMAZON_PROXY_SERVER", "")      # e.g. http://proxy.provider.com:8080
PROXY_USER      = os.getenv("AMAZON_PROXY_USER", "")
PROXY_PASS      = os.getenv("AMAZON_PROXY_PASS", "")

USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:124.0) Gecko/20100101 Firefox/124.0",
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
]


class AmazonScraper(BaseScraper):
    platform = "amazon"

    # ──────────────────────────────────────────
    # PUBLIC ENTRY POINT
    # ──────────────────────────────────────────

    def search(self, query: str) -> list[ScrapedProduct]:
        url = SEARCH_URL + urlencode({"k": query})
        print(f"🔍 Amazon search URL: {url}")

        # 1. Try ScraperAPI if key is set (most reliable, no proxy needed)
        if SCRAPER_API_KEY:
            soup = self._fetch_with_scraperapi(url)
            if soup:
                results = self._parse_search_results(soup, query)
                if len(results) >= 3:
                    print(f"✅ Amazon (ScraperAPI): {len(results)} products")
                    return results

        # 2. Try Playwright with stealth + optional residential proxy
        soup = self._fetch_with_playwright(url)
        if soup:
            results = self._parse_search_results(soup, query)
            if len(results) >= 3:
                print(f"✅ Amazon (Playwright): {len(results)} products")
                return results

        # 3. Fallback to mock data
        print("⚠️  Amazon: All scraping methods failed — using mock data")
        return self._get_mock_data(query)

    # ──────────────────────────────────────────
    # FETCH METHOD 1 — ScraperAPI
    # ──────────────────────────────────────────

    def _fetch_with_scraperapi(self, url: str) -> Optional[BeautifulSoup]:
        """
        Uses ScraperAPI to bypass Amazon blocking.
        Handles JS rendering + residential IPs automatically.
        Sign up free at https://www.scraperapi.com/
        """
        try:
            import requests

            params = {
                "api_key":      SCRAPER_API_KEY,
                "url":          url,
                "render":       "true",       # Execute JavaScript
                "country_code": "in",         # Indian Amazon
                "premium":      "true",       # Residential IPs
            }
            print("🌐 Amazon: Trying ScraperAPI...")
            resp = requests.get(
                "https://api.scraperapi.com/",
                params=params,
                timeout=90,
            )
            if resp.status_code == 200 and len(resp.text) > 5000:
                print("✅ Amazon: ScraperAPI returned valid HTML")
                return BeautifulSoup(resp.text, "html.parser")
            else:
                print(f"⚠️  Amazon: ScraperAPI returned status {resp.status_code}")
        except Exception as e:
            print(f"❌ Amazon ScraperAPI error: {e}")
        return None

    # ──────────────────────────────────────────
    # FETCH METHOD 2 — Playwright + stealth
    # ──────────────────────────────────────────

    def _fetch_with_playwright(self, url: str) -> Optional[BeautifulSoup]:
        """
        Headless Chromium with playwright-stealth + optional residential proxy
        + cookie persistence to look like a returning user.

        Install: pip install playwright-stealth
                 playwright install chromium
        """
        try:
            from playwright.sync_api import sync_playwright

            # Try to import stealth; warn if missing but continue
            try:
                from playwright_stealth import stealth_sync
                HAS_STEALTH = True
            except ImportError:
                print("⚠️  playwright-stealth not installed. Run: pip install playwright-stealth")
                HAS_STEALTH = False

            print("🚀 Amazon: Fetching with Playwright...")

            launch_args = [
                "--no-sandbox",
                "--disable-blink-features=AutomationControlled",
                "--disable-dev-shm-usage",
                "--disable-accelerated-2d-canvas",
                "--no-first-run",
                "--no-zygote",
                "--disable-gpu",
            ]

            with sync_playwright() as p:
                browser = p.chromium.launch(headless=True, args=launch_args)

                # Build context kwargs
                context_kwargs = dict(
                    user_agent=random.choice(USER_AGENTS),
                    locale="en-IN",
                    timezone_id="Asia/Kolkata",
                    viewport={"width": 1366, "height": 768},
                    extra_http_headers={
                        "Accept":                    "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
                        "Accept-Language":           "en-IN,en;q=0.9",
                        "Accept-Encoding":           "gzip, deflate, br",
                        "DNT":                       "1",
                        "Upgrade-Insecure-Requests": "1",
                    },
                )

                # Add residential proxy if configured
                if PROXY_SERVER:
                    print(f"🔒 Amazon: Using proxy: {PROXY_SERVER}")
                    context_kwargs["proxy"] = {
                        "server":   PROXY_SERVER,
                        "username": PROXY_USER,
                        "password": PROXY_PASS,
                    }

                context = browser.new_context(**context_kwargs)

                # ── Stealth patches ──────────────────────────
                # playwright-stealth handles this properly; fallback to manual script
                context.add_init_script("""
                    Object.defineProperty(navigator, 'webdriver', { get: () => undefined });
                    Object.defineProperty(navigator, 'plugins',   { get: () => [1, 2, 3, 4, 5] });
                    Object.defineProperty(navigator, 'languages', { get: () => ['en-IN', 'en'] });
                    window.chrome = { runtime: {} };
                    const orig = window.navigator.permissions.query;
                    window.navigator.permissions.query = p =>
                        p.name === 'notifications'
                            ? Promise.resolve({ state: Notification.permission })
                            : orig(p);
                """)

                # ── Cookie persistence ────────────────────────
                if os.path.exists(COOKIES_FILE):
                    try:
                        with open(COOKIES_FILE) as f:
                            context.add_cookies(json.load(f))
                        print("🍪 Amazon: Loaded saved cookies")
                    except Exception:
                        pass

                page = context.new_page()

                # Apply stealth if available
                if HAS_STEALTH:
                    stealth_sync(page)

                # ── Navigate ──────────────────────────────────
                html = None
                for strategy, timeout in [("domcontentloaded", 20000), ("networkidle", 30000)]:
                    try:
                        print(f"🔄 Trying wait_until={strategy}...")
                        page.goto(url, wait_until=strategy, timeout=timeout)

                        # Abort if CAPTCHA or 503
                        title = page.title()
                        if any(x in title for x in ["503", "Robot Check", "CAPTCHA"]):
                            print(f"⚠️  Blocked page detected ({title}), skipping strategy")
                            continue

                        # Human-like behaviour
                        time.sleep(random.uniform(1.5, 3))
                        page.mouse.move(random.randint(200, 900), random.randint(200, 700))
                        time.sleep(random.uniform(0.5, 1.2))

                        # Wait for product cards
                        found = False
                        for sel in [
                            "div[data-component-type='s-search-result']",
                            "div.s-result-item[data-asin]",
                            "[data-asin]",
                        ]:
                            try:
                                page.wait_for_selector(sel, timeout=8000)
                                print(f"✅ Found results with: {sel}")
                                found = True
                                break
                            except Exception:
                                continue

                        # Scroll to load lazy images
                        for _ in range(3):
                            page.evaluate("window.scrollBy(0, window.innerHeight)")
                            time.sleep(random.uniform(0.8, 1.5))

                        candidate = page.content()
                        if len(candidate) > 5000 and "503" not in candidate[:500]:
                            html = candidate
                            break

                    except Exception as e:
                        print(f"❌ Strategy {strategy} failed: {e}")

                # Save cookies for next run
                try:
                    cookies = context.cookies()
                    with open(COOKIES_FILE, "w") as f:
                        json.dump(cookies, f)
                    print("🍪 Amazon: Cookies saved")
                except Exception:
                    pass

                browser.close()

                if html:
                    return BeautifulSoup(html, "lxml")

        except Exception as e:
            print(f"❌ Amazon Playwright error: {e}")
            import traceback
            traceback.print_exc()

        return None

    # ──────────────────────────────────────────
    # PARSE RESULTS
    # ──────────────────────────────────────────

    def _parse_search_results(self, soup: BeautifulSoup, query: str) -> list[ScrapedProduct]:
        results = []

        # Try selectors from most-to-least specific
        cards = (
            soup.select("div[data-component-type='s-search-result']")
            or soup.select("div.s-result-item[data-asin]")
            or soup.select("div[data-asin]")
            or soup.select("div.sg-col-inner .s-result-item")
        )
        print(f"📊 Amazon: Found {len(cards)} product cards")

        for i, card in enumerate(cards):
            asin = card.get("data-asin", "").strip()
            if not asin:
                continue

            name = self._extract_name(card)
            if not name or len(name) < 5:
                continue

            link_url = self._extract_link(card, asin)
            if not link_url:
                continue

            current_price  = self._extract_price(card, current=True)
            original_price = self._extract_price(card, current=False)

            image_url = ""
            img_el = card.select_one("img.s-image")
            if img_el:
                image_url = self._extract_amazon_image_url(img_el) or ""
            if image_url == "None":
                image_url = ""

            rating = self._extract_rating(card)

            product = ScrapedProduct(
                name=name,
                platform=self.platform,
                listing_url=link_url,
                current_price=current_price,
                original_price=original_price,
                image_url=image_url,
                rating=rating,
            )
            results.append(product)

            if i < 3:
                print(f"  📦 [{i+1}] {name[:60]} | ₹{current_price} | ⭐{rating}")

            if len(results) >= MAX_RESULTS_PER_PLATFORM:
                break

        return results

    # ──────────────────────────────────────────
    # EXTRACTORS (fixed)
    # ──────────────────────────────────────────

    def _extract_name(self, card) -> Optional[str]:
        """Combine all h2 text nodes — Amazon sometimes splits names across elements."""
        h2_list = card.select("h2")
        if not h2_list:
            return None
        parts = [h2.get_text(strip=True) for h2 in h2_list if h2.get_text(strip=True)]
        return " ".join(parts) if parts else None

    def _extract_link(self, card, asin: str) -> Optional[str]:
        """Find the canonical /dp/ product URL."""
        # Primary: anchor that contains /dp/<ASIN>
        for a in card.select("a[href]"):
            href = a.get("href", "")
            if f"/dp/{asin}" in href:
                clean = href.split("?")[0]
                return urljoin(AMAZON_BASE, clean)

        # Secondary: any anchor with /dp/ pattern
        for a in card.select("a[href]"):
            href = a.get("href", "")
            if "/dp/" in href:
                clean = href.split("?")[0]
                return urljoin(AMAZON_BASE, clean)

        # Fallback: construct from ASIN
        if asin:
            return f"{AMAZON_BASE}/dp/{asin}"

        return None

    def _extract_price(self, container, current: bool) -> Optional[int]:
        """Extract current or original/strike-through price."""
        if current:
            # Most reliable: whole-price span
            whole = container.select_one("span.a-price-whole")
            if whole:
                text = whole.get_text(strip=True).rstrip(".")
                price = self.parse_price(text)
                if price:
                    return price

            # Fallbacks
            for sel in [
                "span.a-price[data-a-color='base'] span.a-offscreen",
                "span.a-price span.a-offscreen",
                "#priceblock_ourprice",
                "#priceblock_dealprice",
            ]:
                el = container.select_one(sel)
                if el:
                    price = self.parse_price(el.get_text(strip=True))
                    if price:
                        return price
        else:
            for sel in [
                "span.a-price[data-a-color='secondary'] span.a-offscreen",
                "span.a-text-price span.a-offscreen",
            ]:
                el = container.select_one(sel)
                if el:
                    price = self.parse_price(el.get_text(strip=True))
                    if price:
                        return price

        return None

    def _extract_rating(self, container) -> Optional[float]:
        """Try multiple selectors — Amazon changes these frequently."""
        # aria-label on links: "4.2 out of 5 stars"
        for el in container.select("a[aria-label], span[aria-label]"):
            label = el.get("aria-label", "")
            m = re.search(r"(\d+(?:\.\d+)?)\s+out\s+of\s+5", label)
            if m:
                return float(m.group(1))

        # span.a-icon-alt text
        rating_el = container.select_one("span.a-icon-alt, i.a-icon-star span.a-icon-alt")
        if rating_el:
            m = re.search(r"(\d+(?:\.\d+)?)", rating_el.get_text())
            if m:
                return float(m.group(1))

        return None

    def _extract_amazon_image_url(self, img_el) -> Optional[str]:
        """Extract highest-resolution image URL from srcset or fallback attributes."""
        if not img_el:
            return None

        image_url = None

        # 1. srcset — pick highest multiplier
        srcset = img_el.get("srcset", "")
        if srcset:
            best_url, best_x = None, 0.0
            for entry in srcset.split(","):
                parts = entry.strip().split()
                if len(parts) >= 2:
                    try:
                        x = float(parts[1].rstrip("x"))
                        if x > best_x:
                            best_x, best_url = x, parts[0]
                    except ValueError:
                        continue
            if best_url:
                image_url = best_url

        # 2. Fallback attributes
        if not image_url:
            for attr in ("src", "data-src", "data-old-hires"):
                val = img_el.get(attr)
                if val:
                    image_url = val
                    break

        # 3. data-a-dynamic-image (JSON map of url→[w,h])
        if not image_url:
            dyn = img_el.get("data-a-dynamic-image", "")
            if dyn:
                try:
                    data = json.loads(dyn.replace("&quot;", '"'))
                    if isinstance(data, dict):
                        # Pick largest by area
                        best = max(data.items(), key=lambda kv: kv[1][0] * kv[1][1])
                        image_url = best[0]
                except Exception:
                    pass

        if not image_url:
            return None

        # Normalise protocol
        if image_url.startswith("//"):
            image_url = "https:" + image_url

        # Normalise domain variants
        for pattern, replacement in [
            (r"https?://[^/]*images-amazon\.com/", "https://m.media-amazon.com/"),
            (r"https?://[^/]*amazon\.com/images/", "https://m.media-amazon.com/images/"),
        ]:
            image_url = re.sub(pattern, replacement, image_url)

        return image_url

    # ──────────────────────────────────────────
    # PRODUCT PAGE
    # ──────────────────────────────────────────

    def get_product(self, url: str) -> Optional[ScrapedProduct]:
        soup = self._get(url)
        if not soup:
            return None

        name_el = soup.select_one("#productTitle, #title span")
        name = name_el.get_text(strip=True) if name_el else None
        if not name:
            return None

        current_price  = self._extract_price(soup, current=True)
        original_price = self._extract_price(soup, current=False)

        image_url = None
        img_el = soup.select_one("#landingImage, #imgBlkFront")
        if img_el:
            image_url = img_el.get("src") or img_el.get("data-old-hires")

        out_of_stock = bool(soup.select_one("#outOfStock, #availability span.a-color-error"))

        brand_el = soup.select_one("#bylineInfo, #brand")
        brand = None
        if brand_el:
            brand = (
                brand_el.get_text(strip=True)
                .replace("Brand: ", "")
                .replace("Visit the ", "")
                .replace(" Store", "")
            )

        return ScrapedProduct(
            name=name,
            platform=self.platform,
            listing_url=url,
            current_price=current_price,
            original_price=original_price,
            image_url=image_url,
            brand=brand,
            in_stock=not out_of_stock,
        )

    # ──────────────────────────────────────────
    # MOCK DATA FALLBACK
    # ──────────────────────────────────────────

    def _get_mock_data(self, query: str) -> list[ScrapedProduct]:
        mock_db = {
            "iphone": [
                {"name": "Apple iPhone 15 (128 GB) - Black",             "price": 59999,  "original_price": 69999,  "rating": 4.6, "image": "https://m.media-amazon.com/images/I/61bBi+BL+kL._SX679_.jpg"},
                {"name": "Apple iPhone 14 (128 GB) - Blue",              "price": 54999,  "original_price": 64999,  "rating": 4.5, "image": "https://m.media-amazon.com/images/I/61cTxVthCBL._SX679_.jpg"},
                {"name": "Apple iPhone 13 (128 GB) - Pink",              "price": 49999,  "original_price": 59999,  "rating": 4.4, "image": "https://m.media-amazon.com/images/I/61v7Q9R2h9L._SX679_.jpg"},
                {"name": "Apple iPhone 15 Pro (256 GB) - Natural Titanium","price": 119999, "original_price": 139999, "rating": 4.7, "image": "https://m.media-amazon.com/images/I/61QJ5woYjTL._SX679_.jpg"},
                {"name": "Apple iPhone 12 (64 GB) - White",              "price": 42999,  "original_price": 52999,  "rating": 4.3, "image": "https://m.media-amazon.com/images/I/71XB8h7dDIL._SX679_.jpg"},
            ],
            "laptop": [
                {"name": "HP Pavilion 14 (Intel Core i5-1135G7)",        "price": 44999,  "original_price": 54999,  "rating": 4.2, "image": "https://m.media-amazon.com/images/I/71WvQ3yL1WL._SX679_.jpg"},
                {"name": "Lenovo IdeaPad Slim 3 (Intel Core i3-11th Gen)","price": 34999,  "original_price": 42999,  "rating": 4.1, "image": "https://m.media-amazon.com/images/I/61QJ5woYjTL._SX679_.jpg"},
                {"name": "Dell Vostro 3401 (Intel Core i5-11th Gen)",     "price": 49999,  "original_price": 59999,  "rating": 4.0, "image": "https://m.media-amazon.com/images/I/61bBi+BL+kL._SX679_.jpg"},
                {"name": "ASUS VivoBook 15 (Intel Core i3-10th Gen)",     "price": 29999,  "original_price": 35999,  "rating": 3.9, "image": "https://m.media-amazon.com/images/I/61cTxVthCBL._SX679_.jpg"},
                {"name": "Acer Aspire 3 (AMD Ryzen 5)",                  "price": 37999,  "original_price": 45999,  "rating": 4.1, "image": "https://m.media-amazon.com/images/I/61v7Q9R2h9L._SX679_.jpg"},
            ],
            "headphones": [
                {"name": "Sony WH-CH520 Wireless Bluetooth Headphones",  "price": 4999,   "original_price": 6999,   "rating": 4.3, "image": "https://m.media-amazon.com/images/I/61QJ5woYjTL._SX679_.jpg"},
                {"name": "boAt Rockerz 450 Bluetooth Headphones",        "price": 1499,   "original_price": 2999,   "rating": 4.0, "image": "https://m.media-amazon.com/images/I/61bBi+BL+kL._SX679_.jpg"},
                {"name": "JBL Tune 510BT Wireless Headphones",           "price": 2999,   "original_price": 4999,   "rating": 4.2, "image": "https://m.media-amazon.com/images/I/61cTxVthCBL._SX679_.jpg"},
                {"name": "Bose QuietComfort 45 Headphones",              "price": 24999,  "original_price": 32999,  "rating": 4.6, "image": "https://m.media-amazon.com/images/I/61v7Q9R2h9L._SX679_.jpg"},
                {"name": "OnePlus Bullets Wireless Z2",                  "price": 1999,   "original_price": 2999,   "rating": 4.1, "image": "https://m.media-amazon.com/images/I/71WvQ3yL1WL._SX679_.jpg"},
            ],
        }

        products = mock_db.get(query.lower(), [])

        # Generic fallback
        if not products:
            products = [
                {
                    "name":           f"{query.title()} Product {i+1} (Amazon)",
                    "price":          random.randint(999, 49999),
                    "original_price": random.randint(5000, 60000),
                    "rating":         round(random.uniform(3.5, 4.8), 1),
                    "image":          "https://m.media-amazon.com/images/I/61bBi+BL+kL._SX679_.jpg",
                }
                for i in range(5)
            ]

        results = []
        for i, p in enumerate(products):
            results.append(ScrapedProduct(
                name=p["name"],
                platform="amazon",
                listing_url=f"https://www.amazon.in/dp/MOCK{query.replace(' ', '')}{i}",
                current_price=p["price"],
                original_price=p["original_price"],
                image_url=p["image"],
                rating=p["rating"],
            ))
            print(f"  📦 Mock [{i+1}] {p['name'][:55]} | ₹{p['price']} | ⭐{p['rating']}")

        print(f"✅ Amazon mock: {len(results)} products for '{query}'")
        return results