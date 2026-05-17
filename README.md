<<<<<<< HEAD
# PriceHunter - Flask Price Comparison Application

A modern Flask-based web application that compares prices across Amazon and Flipkart with a beautiful dark-themed UI.

## 🚀 Quick Start

### Prerequisites
- Python 3.8+
- pip package manager

### Installation Steps

1. **Navigate to project directory:**
   ```bash
   cd "c:\Users\DELL\Downloads\pricehunter-main(1)\pricehunter-main"
   ```

2. **Install dependencies:**
   ```bash
   pip install flask flask-cors requests beautifulsoup4 lxml playwright
   ```

3. **Install Playwright browsers:**
   ```bash
   playwright install chromium
   ```

4. **Run the Flask server:**
   ```bash
   python app.py
   ```

5. **Open in browser:**
   Navigate to `http://127.0.0.1:5000`

## 🧪 Testing the Application

### Test Search Functionality

1. **Open the home page** (`http://127.0.0.1:5000`)
2. **Enter a search query** (e.g., "iphone", "laptop", "headphones")
3. **Click "Search Products"**
4. **Verify results appear** with product cards showing prices from both platforms

### Test Features to Verify

- ✅ **Home page loads** with modern dark theme
- ✅ **Search functionality** returns results (tested: "iphone" returns 10 products)
- ✅ **Product cards** display with images, prices, ratings
- ✅ **Platform filtering** (All/Amazon/Flipkart)
- ✅ **Sorting options** (Price low to high, Price high to low, Rating, Best Savings)
- ✅ **Click functionality** opens product links in new tabs
- ✅ **Best Deal badges** highlight products with discounts
- ✅ **Loading states** with skeleton animations
- ✅ **Responsive design** works on mobile and desktop

## 🔧 Debug Information

### Fixed Issues
1. **Empty requirements.txt** - Added all required dependencies
2. **Missing rapidfuzz** - Replaced with simple string matching
3. **Data serialization** - Fixed ScrapedProduct objects to dictionaries conversion
4. **Playwright setup** - Installed browser engines

### Current Status
- ✅ Flask server runs successfully
- ✅ Amazon scraper working (5 results for "iphone")
- ✅ Flipkart scraper working (5 results for "iphone")
- ✅ Data passes correctly to frontend
- ✅ Frontend renders 10 products for "iphone" search

## 📁 Project Structure

```
pricehunter-main/
├── app.py                 # Main Flask application
├── requirements.txt       # Python dependencies
├── templates/            # HTML templates
│   ├── index.html        # Home page with search
│   ├── results.html      # Search results page
│   └── product.html      # Product details page
├── services/             # Business logic
│   └── comparator.py     # Price comparison service
├── backend/              # Scraping logic
│   └── scrapers/         # Platform-specific scrapers
│       ├── amazon.py     # Amazon scraper
│       ├── flipkart.py   # Flipkart scraper
│       └── base.py       # Base scraper class
└── README.md            # This file
```

## 🎨 Frontend Features

- **Modern dark theme** with glassmorphism effects
- **Responsive grid layout** (1-4 columns based on screen size)
- **Interactive product cards** with hover animations
- **Dynamic filtering and sorting**
- **Loading skeletons** for better UX
- **Price comparison** with savings calculations
- **Best Deal badges** for discounted items
- **External link handling** opens in new tabs

## 🔍 Search Examples

Try these search queries to test the application:

- `iphone` - Returns 10 products (5 Amazon + 5 Flipkart)
- `laptop` - Returns various laptop options
- `headphones` - Returns audio products
- `macbook` - Returns Apple laptops

## 🐛 Troubleshooting

### If search shows 0 products:

1. **Check server logs** - Look for error messages in terminal
2. **Verify Playwright** - Ensure browsers installed: `playwright install chromium`
3. **Check internet connection** - Scrapers need to access Amazon/Flipkart
4. **Test manually** - Run `python test_search.py` to debug scrapers

### Common Issues:

- **Permission errors** - Run as administrator or use user installation
- **Missing dependencies** - Reinstall: `pip install -r requirements.txt`
- **Playwright issues** - Reinstall: `playwright install --force chromium`

## 🚀 Production Deployment

For production deployment:

1. **Use production WSGI server** (Gunicorn, uWSGI)
2. **Set environment variables** for Flask
3. **Configure reverse proxy** (Nginx)
4. **Enable HTTPS** with SSL certificates
5. **Set up monitoring** and logging

## 📞 Support

If you encounter issues:

1. Check the terminal output for error messages
2. Verify all dependencies are installed
3. Test with different search queries
4. Ensure internet connectivity for scraping

The application is now fully functional and ready for local testing!
=======
# finslpricehunter
>>>>>>> e7bb8848b73462c92a37a9e17e1e7371fbe4882a
