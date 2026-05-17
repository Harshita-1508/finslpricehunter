import re
from typing import Optional
from urllib.parse import urlencode, urljoin

from backend.scrapers.base import BaseScraper, ScrapedProduct
from backend.config import MAX_RESULTS_PER_PLATFORM

FLIPKART_BASE = "https://www.flipkart.com"
SEARCH_URL = f"{FLIPKART_BASE}/search?"


class FlipkartScraper(BaseScraper):
    platform = "flipkart"

    def search(self, query: str) -> list[ScrapedProduct]:
        url = SEARCH_URL + urlencode({"q": query, "marketplace": "FLIPKART"})
        soup = self._get(url)
        if not soup:
            return []

        results = []
        seen_urls = set()

        # ── Strategy 1: collect every unique /p/ link ──────────────────────
        # Flipkart uses both /p/ and /<slug>/p/ patterns; match both.
        product_links = soup.find_all(
            "a", href=re.compile(r"/p/[A-Z0-9]{6,}", re.IGNORECASE)
        )
        print(f"Flipkart /p/ links found: {len(product_links)}")

        for link in product_links:
            href = link.get("href", "")
            base_href = href.split("?")[0]
            if base_href in seen_urls:
                continue
            seen_urls.add(base_href)
            full_url = urljoin(FLIPKART_BASE, base_href)

            link_text = link.get_text(separator=" ", strip=True)

            # Skip "currently unavailable" listings
            if "currently unavailable" in link_text.lower():
                continue

            # Walk up to find the card container
            container = self._find_card_container(link)

            name = self._extract_name(link, container)
            if not name or len(name) < 5:
                continue

            current_price = self._find_price_in_tree(container, is_current=True)
            original_price = self._find_price_in_tree(container, is_current=False)
            image_url = self._find_image(container)

            rating = None
            rating_el = container.select_one("div.XQDdHH")

            if rating_el:
                try:
                    rating = float(rating_el.get_text())
                except:
                    
                    pass

            results.append(ScrapedProduct(
                name=name,
                platform=self.platform,
                listing_url=full_url,
                current_price=current_price,
                original_price=original_price,
                image_url=image_url,
                rating=rating 
            ))

            if len(results) >= MAX_RESULTS_PER_PLATFORM:
                break

        # ── Strategy 2: fallback — scrape grid/list item containers directly ─
        if not results:
            print("Flipkart: primary strategy yielded nothing, trying container fallback")
            results = self._scrape_via_containers(soup, seen_urls)

        return results

    # ── Fallback: find product cards by structural heuristics ───────────────
    def _scrape_via_containers(self, soup, seen_urls: set) -> list[ScrapedProduct]:
        results = []

        # Flipkart wraps each search result in a div that contains exactly one
        # product title, one price, and one /p/ link.  We look for any div that
        # has a ₹ symbol AND a /p/ link inside it, then walk UP until we reach
        # the outermost such div (the card).
        candidates = set()
        for price_el in soup.find_all(string=re.compile(r"₹[\d,]+")):
            node = price_el.parent
            for _ in range(12):
                if node is None or node.name in ("body", "html"):
                    break
                if node.name == "div" and node.find("a", href=re.compile(r"/p/")):
                    candidates.add(id(node))
                    # keep walking up to grab the outermost matching div
                node = node.parent

        visited_ids = set()
        for price_el in soup.find_all(string=re.compile(r"₹[\d,]+")):
            card = None
            node = price_el.parent
            for _ in range(12):
                if node is None or node.name in ("body", "html"):
                    break
                if node.name == "div" and id(node) in candidates:
                    card = node
                node = node.parent

            if card is None or id(card) in visited_ids:
                continue
            visited_ids.add(id(card))

            link = card.find("a", href=re.compile(r"/p/"))
            if not link:
                continue

            href = link.get("href", "").split("?")[0]
            if href in seen_urls:
                continue
            seen_urls.add(href)
            full_url = urljoin(FLIPKART_BASE, href)

            name = self._extract_name(link, card)
            if not name or len(name) < 5:
                continue

            current_price = self._find_price_in_tree(card, is_current=True)
            original_price = self._find_price_in_tree(card, is_current=False)
            image_url = self._find_image(card)

            results.append(ScrapedProduct(
                name=name,
                platform=self.platform,
                listing_url=full_url,
                current_price=current_price,
                original_price=original_price,
                image_url=image_url,
            ))

            if len(results) >= MAX_RESULTS_PER_PLATFORM:
                break

        return results

    def get_product(self, url: str) -> Optional[ScrapedProduct]:
        soup = self._get(url)
        if not soup:
            return None

        # ── Name ─────────────────────────────────────────────────────────────
        name = None
        # Try a broad set of class patterns (Flipkart renames these often)
        for sel in [
            "span.VU-ZEz", "span.B_NuCI", "h1._35KyD6",
            "h1.yhB1nd", "span.G6XhRU",
        ]:
            el = soup.select_one(sel)
            if el:
                name = el.get_text(strip=True)
                break
        if not name:
            h1 = soup.select_one("h1")
            if h1:
                name = h1.get_text(strip=True)
        if not name:
            return None

        current_price = self._find_price_in_tree(soup, is_current=True)
        original_price = self._find_price_in_tree(soup, is_current=False)

        # ── Image ─────────────────────────────────────────────────────────────
        image_url = None
        for sel in ["img._396cs4", "img._2r_T1I", "img.DByuf4", "img.sza_g4"]:
            img_el = soup.select_one(sel)
            if img_el:
                image_url = img_el.get("src") or img_el.get("data-src")
                break
        if not image_url:
            for img in soup.select("img[src]"):
                src = img.get("src", "")
                if "rukminim" in src or "flixcart" in src:
                    image_url = src
                    break

        out_of_stock = bool(soup.select_one("div._16FRp0"))

        return ScrapedProduct(
            name=name,
            platform=self.platform,
            listing_url=url,
            current_price=current_price,
            original_price=original_price,
            image_url=image_url,
            in_stock=not out_of_stock,
        )

    # ── Helpers ──────────────────────────────────────────────────────────────

    def _extract_name(self, link, container=None) -> Optional[str]:
        """
        Multi-strategy name extraction, most-reliable first.
        """
        root = container if container is not None else link

        # 1. Known class selectors (try inside the card container)
        for sel in [
            "div.KzDlHZ", "div.RG5Slk", "div._4rR01T",
            "a.s1Q9rs", "a.WKTcLC", "div.iN9qNs",
            # Broad fallback: any div/span whose text looks like a product name
        ]:
            el = root.select_one(sel) if root else None
            if el:
                text = el.get_text(strip=True)
                if len(text) > 5:
                    return text[:120]

        # 2. Walk parents of the link looking for name-class elements
        node = link
        for _ in range(8):
            if node is None:
                break
            for sel in ["div.KzDlHZ", "div.RG5Slk", "div._4rR01T", "a.s1Q9rs", "a.WKTcLC"]:
                el = node.select_one(sel)
                if el:
                    text = el.get_text(strip=True)
                    if len(text) > 5:
                        return text[:120]
            node = node.parent

        # 3. The link's own text is often the full product blob — clean it up
        text = link.get_text(separator=" ", strip=True)
        text = re.sub(r"^Add to Compare\s*", "", text, flags=re.IGNORECASE)

        # Cut at rating/review patterns: "4.3 (12,345 Ratings)"
        text = re.split(r"\d\.\d[\d,]*\s*\(?\s*[\d,]+\s*Ratings?\)?", text, flags=re.IGNORECASE)[0]
        # Cut at spec patterns like "128 GB ROM", "8 GB RAM"
        text = re.split(r"\b\d+\s*GB\s*(ROM|RAM|Storage|SSD)\b", text, flags=re.IGNORECASE)[0]
        # Cut at price
        text = re.split(r"₹[\d,]+", text)[0]
        text = text.strip()

        if len(text) > 10:
            return text[:120]

        # 4. Use the href slug as last resort
        href = link.get("href", "")
        slug_match = re.search(r"/([^/]+)/p/", href)
        if slug_match:
            slug = slug_match.group(1).replace("-", " ").title()
            if len(slug) > 5:
                return slug[:120]

        return None

    def _find_card_container(self, link):
        """
        Walk UP from a product link until we find the div that most tightly
        wraps the entire card (title + price + image).

        Old logic required exactly 1 /p/ link — too strict.  New logic:
        stop at the first ancestor div that contains AT LEAST one ₹ price
        AND an img, unless we've already walked 12 levels up.
        """
        node = link
        best = link.parent  # safe fallback

        for _ in range(12):
            if node is None or node.name in ("body", "html"):
                break
            node = node.parent
            if not node or node.name != "div":
                continue

            has_price = bool(node.find(string=re.compile(r"₹[\d,]+")))
            has_img = bool(node.find("img"))

            if has_price and has_img:
                best = node
                # Don't break — keep going up so we grab the outermost card div
                # that still has ONLY this product's data.
                # Stop if the next level would add a second /p/ link from a
                # *different* product.
                parent = node.parent
                if parent and parent.name == "div":
                    sibling_links = parent.find_all(
                        "a", href=re.compile(r"/p/[A-Z0-9]{6,}", re.IGNORECASE)
                    )
                    # More than ~4 /p/ links means we've hit the grid wrapper
                    if len(sibling_links) > 4:
                        break

        return best

    def _find_price_in_tree(self, container, is_current: bool) -> Optional[int]:
        """
        Two-pass price extraction:
          Pass 1 — try known class selectors.
          Pass 2 — collect ALL ₹ prices in the container, then decide which
                   is current vs original by position / value heuristics.
        """
        if not container:
            return None

        # Pass 1: class-based selectors
        if is_current:
            selectors = [
                "div.Nx9bqj", "div._30jeq3", "div.hZ3P6w",
                "div._1_WHN1", "div.hl05eU div.Nx9bqj",
            ]
        else:
            selectors = [
                "div.yRaY8j", "div._3I9_wc", "div.kRYCnD",
                "div._27UcVY", "div.hl05eU div.yRaY8j",
            ]

        for sel in selectors:
            el = container.select_one(sel)
            if el:
                price = self._parse_price_text(el.get_text(strip=True))
                if price:
                    return price

        # Pass 2: collect all raw ₹ amounts in document order
        raw_prices: list[int] = []
        for el in container.find_all(string=re.compile(r"₹[\d,]+")):
            m = re.search(r"₹([\d,]+)", str(el))
            if m:
                val = int(m.group(1).replace(",", ""))
                if val > 0:
                    raw_prices.append(val)

        if not raw_prices:
            return None

        # Deduplicate preserving order
        seen: set[int] = set()
        unique_prices: list[int] = []
        for p in raw_prices:
            if p not in seen:
                seen.add(p)
                unique_prices.append(p)

        if is_current:
            # Current price is typically the LOWEST (after discounts)
            return min(unique_prices)
        else:
            # Original / MRP is typically the HIGHEST
            if len(unique_prices) >= 2:
                return max(unique_prices)
            return None  # Only one price found — no original to report

    def _find_image(self, container) -> Optional[str]:
        if not container:
            return None
        for sel in ["img._396cs4", "img._2r_T1I", "img.DByuf4", "img.sza_g4", "img"]:
            img = container.select_one(sel)
            if img:
                src = img.get("src") or img.get("data-src") or ""
                if src and not src.startswith("data:") and "svg" not in src:
                    return src
        return None

    @staticmethod
    def _parse_price_text(text: str) -> Optional[int]:
        """Extract an integer rupee amount from a price string."""
        if not text:
            return None
        m = re.search(r"₹?([\d,]+)", text)
        if m:
            val = int(m.group(1).replace(",", ""))
            return val if val > 0 else None
        return None