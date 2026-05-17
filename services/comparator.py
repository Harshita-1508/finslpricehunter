from backend.scrapers.amazon import AmazonScraper
from backend.scrapers.flipkart import FlipkartScraper
from concurrent.futures import ThreadPoolExecutor

cache = {}
class PriceComparator:
    def __init__(self):
        self.amazon = AmazonScraper()
        self.flipkart = FlipkartScraper()
    
    def search_all(self, query):
        global cache

    # 🔥 CHECK CACHE FIRST
        if query in cache:
            print("⚡ Using cached results")
            return cache[query]
        print("\n==============================")
        print("SEARCH QUERY:", query)
        print("==============================")

        with ThreadPoolExecutor(max_workers=2) as executor:
            amazon_future = executor.submit(self.amazon.search, query)
            flipkart_future = executor.submit(self.flipkart.search, query)

            try:
                amazon_results = amazon_future.result()
            except:
                amazon_results = []

            try:
                flipkart_results = flipkart_future.result()
            except:
                flipkart_results = []

        # 📊 Step 2: Debug counts
        print("Amazon results:", len(amazon_results))
        print("Flipkart results:", len(flipkart_results))

        # 🔗 Step 3: Combine results
        combined = amazon_results + flipkart_results

        print("Total before filtering:", len(combined))

        # 🧹 Step 4: Remove items without price
        combined = [p for p in combined if p.current_price]

        print("After removing no-price items:", len(combined))

        # 💰 Step 5: Sort by price (lowest first)
        combined.sort(key=lambda x: x.current_price)

        # 🏆 Step 6: Print top 3 cheapest (debug)
        print("\nTop cheapest products:")
        for p in combined[:3]:
            print(f"{p.name[:50]} | ₹{p.current_price} | {p.platform}")

        print("==============================\n")
        cache[query] = combined

        return combined

import re

def find_best_match(target_name, products):
    best = None
    best_score = 0

    for p in products:
        # Simple string similarity based on word overlap
        target_words = set(re.findall(r'\w+', target_name.lower()))
        product_words = set(re.findall(r'\w+', p.name.lower()))
        
        if not target_words or not product_words:
            continue
            
        # Calculate Jaccard similarity
        intersection = len(target_words & product_words)
        union = len(target_words | product_words)
        score = (intersection / union) * 100 if union > 0 else 0

        if score > best_score:
            best_score = score
            best = p

    # avoid wrong matches
    if best_score > 30:  # Lower threshold for simple matching
        return best

    return None