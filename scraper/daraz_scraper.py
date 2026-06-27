"""
Daraz Nepal Scraper
--------------------
Scrapes product name, price, and rating for given search terms from Daraz.com.np
Uses Selenium because Daraz pages are JavaScript-rendered (plain requests won't see the products).
 
Run modes:
  1. Default mode  -> scrapes a fixed list of categories (consistent dataset for ML training)
  2. Custom mode    -> type your own category live from the terminal (good for demo/viva)
"""
 
import time
import csv
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
 
 
DEFAULT_CATEGORIES = ["smartphone", "laptop", "smartwatch", "earphone", "tablet"]
 
 
def setup_driver():
    """Sets up a Chrome browser instance controlled by Selenium."""
    options = Options()
    options.add_argument("--headless=new")
    options.add_argument("--disable-gpu")
    options.add_argument("--window-size=1920,1080")
    options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36")
 
    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=options)
    return driver
 
 
def scrape_daraz(search_term, max_products=20):
    """
    Scrapes Daraz search results for a given search term.
    Returns a list of dictionaries: [{name, price, marketplace, search_term, link}, ...]
    """
    driver = setup_driver()
    url = f"https://www.daraz.com.np/catalog/?q={search_term.replace(' ', '+')}"
    print(f"Opening: {url}")
    driver.get(url)
 
    time.sleep(5)
 
    products = []
 
    try:
        items = driver.find_elements(By.CSS_SELECTOR, "[data-qa-locator='product-item']")
        print(f"Found {len(items)} product cards on page")
 
        for item in items[:max_products]:
            name = "N/A"
            try:
                name = item.find_element(By.CSS_SELECTOR, "a[title]").get_attribute("title")
            except Exception:
                pass
 
            if name == "N/A" or not name:
                try:
                    name = item.find_element(By.CSS_SELECTOR, "[title]").get_attribute("title")
                except Exception:
                    pass
 
            if name == "N/A" or not name:
                try:
                    name = item.find_element(By.CSS_SELECTOR, "img").get_attribute("alt")
                except Exception:
                    pass
 
            try:
                price = item.find_element(By.CSS_SELECTOR, ".currency--wrapper, .aBrP0").text
            except Exception:
                price = "N/A"
 
            try:
                link = item.find_element(By.TAG_NAME, "a").get_attribute("href")
            except Exception:
                link = "N/A"
 
            products.append({
                "product_name": name,
                "price": price,
                "marketplace": "Daraz",
                "search_term": search_term,
                "link": link
            })
 
    except Exception as e:
        print(f"Error while scraping: {e}")
 
    driver.quit()
    return products
 
 
def save_to_csv(products, filename="data/raw/daraz_scraped.csv"):
    """Saves scraped product list to a CSV file."""
    if not products:
        print("No products to save.")
        return
 
    keys = products[0].keys()
    with open(filename, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=keys)
        writer.writeheader()
        writer.writerows(products)
 
    print(f"Saved {len(products)} products to {filename}")
 
 
def get_categories_from_user():
    """
    Asks the user in the terminal whether to use the default category list
    or type in custom categories.
    """
    print("\n--- Daraz Scraper ---")
    print(f"Default categories: {', '.join(DEFAULT_CATEGORIES)}")
    choice = input("Press ENTER to use default categories, or type your own (comma-separated): ").strip()
 
    if choice == "":
        return DEFAULT_CATEGORIES
    else:
        custom = [c.strip() for c in choice.split(",") if c.strip()]
        return custom
 
 
if __name__ == "__main__":
    categories = get_categories_from_user()
    print(f"\nWill scrape these categories: {categories}")
 
    all_products = []
 
    for category in categories:
        print(f"\n--- Scraping category: {category} ---")
        results = scrape_daraz(category, max_products=20)
        all_products.extend(results)
        time.sleep(3)
 
    print(f"\nTotal products scraped: {len(all_products)}")
    save_to_csv(all_products, filename="data/raw/daraz_scraped.csv")