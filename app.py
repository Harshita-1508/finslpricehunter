from flask import Flask, render_template, request
from services.comparator import PriceComparator, find_best_match

app = Flask(__name__)
comparator = PriceComparator()

def safe_int(val):
    """Safely convert value to integer"""
    try:
        if val and val != "None":
            return int(val)
    except (ValueError, TypeError):
        pass
    return None


@app.route("/")
def home():
    # Check for theme preference (default to light theme)
    theme = request.args.get('theme', 'light')
    template = "index_light.html" if theme == 'light' else "index.html"
    return render_template(template)


@app.route("/search", methods=["POST"])
def search():
    query = request.form.get("query")
    theme = request.form.get("theme", "light")
    print(f"🔍 Search query received: {query}")
    
    results = comparator.search_all(query)
    print(f"📊 Found {len(results)} raw results")
    
    # Convert ScrapedProduct objects to dictionaries for JSON serialization
    results_dict = []
    for result in results:
        result_dict = {
            'name': result.name,
            'platform': result.platform,
            'current_price': result.current_price,
            'original_price': result.original_price,
            'listing_url': result.listing_url,
            'image_url': result.image_url,
            'brand': result.brand,
            'in_stock': result.in_stock,
            'rating': result.rating
        }
        results_dict.append(result_dict)
    
    print(f"📋 Converted {len(results_dict)} results to dictionaries")
    
    # Debug: Print first result
    if results_dict:
        print(f"🔍 First result: {results_dict[0]['name'][:50]}... | ₹{results_dict[0]['current_price']} | {results_dict[0]['platform']}")
    
    # Choose template based on theme
    template = "results_light.html" if theme == "light" else "results.html"
    return render_template(template, results=results_dict, query=query)


@app.route("/product")
def product():
    name = request.args.get("name")
    platform = request.args.get("platform")
    
    # Use safe helper functions for type conversion
    current_price = safe_int(request.args.get("current_price"))
    original_price = safe_int(request.args.get("original_price"))
    
    # Fix rating conversion
    try:
        rating = float(request.args.get("rating")) if request.args.get("rating") else None
    except (ValueError, TypeError):
        rating = None
    
    image_url = request.args.get("image_url")
    listing_url = request.args.get("listing_url")
    in_stock = request.args.get("in_stock", "true").lower() == "true"
    theme = request.args.get("theme", "light")

    # Create current product object
    current_product = {
        "platform": platform,
        "url": listing_url,
        "price": current_price
    }
    
    # 🔥 Only search other platform (FAST)
    other_product = None
    clean_query = " ".join(name.split()[:3])
    if platform == "amazon":
        other_results = comparator.flipkart.search(clean_query)
    else:
        other_results = comparator.amazon.search(clean_query)

    # 🔍 find best match
    match = None

    if other_results:
        current_name = name.lower()

    # Extract important keywords
        keywords = []

        for word in current_name.split():
            if (
                len(word) > 2 and
                word not in ["with", "for", "and", "the", "inch"]
            ):
                keywords.append(word)

        best_score = 0

        for product in other_results:
            product_name = product.name.lower()

            score = 0

        # keyword matching
            for keyword in keywords:
                if keyword in product_name:
                    score += 1

        # bonus for exact storage match
            for storage in ["64", "128", "256", "512", "1tb"]:
                if storage in current_name and storage in product_name:
                    score += 3

        # bonus for color match
            colors = ["black", "blue", "white", "green", "silver", "gold"]
            for color in colors:
                if color in current_name and color in product_name:
                    score += 2

            if score > best_score:
                best_score = score
                match = product

    if match:
        other_product = {
            "platform": match.platform,
            "url": match.listing_url,
            "price": match.current_price
        }

    # discount logic (optional)
    discount = None
    if current_price is not None and original_price is not None:
        try:
            if original_price > current_price:
                discount = round(((original_price - current_price) / original_price) * 100)
        except:
            pass

    # Choose template based on theme
    template = "product_light.html" if theme == "light" else "product.html"
    
    return render_template(
        template,
        name=name,
        platform=platform,
        current_price=current_price,
        original_price=original_price,
        image_url=image_url,
        listing_url=listing_url,
        in_stock=in_stock,
        rating=rating,
        discount=discount,
        current_product=current_product,
        other_product=other_product
    )


# 🚀 IMPORTANT: THIS WAS MISSING
import os

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)