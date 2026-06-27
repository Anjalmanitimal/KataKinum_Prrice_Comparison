import time
import csv
import re
from datetime import datetime

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager


OLIZ_URL = "https://olizstore.com/products"


def setup_driver():
    options = Options()

    options.add_argument("--headless=new")
    options.add_argument("--disable-gpu")
    options.add_argument("--window-size=1920,1080")

    options.add_argument(
        "user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/137.0 Safari/537.36"
    )

    driver = webdriver.Chrome(
        service=Service(ChromeDriverManager().install()),
        options=options
    )

    return driver


def scrape_oliz(max_products=200):

    driver = setup_driver()

    print(f"Opening: {OLIZ_URL}")

    driver.get(OLIZ_URL)

    time.sleep(10)

    page = driver.page_source

    with open("oliz_debug.html", "w", encoding="utf-8") as f:
        f.write(page)

    print("Saved page source to oliz_debug.html")

    driver.quit()

    products = []

    pattern = r'"name":"([^"]+)".*?"slug":"([^"]+)".*?"price":(\d+)'

    matches = re.findall(
        pattern,
        page,
        re.DOTALL
    )

    print(f"Raw matches found: {len(matches)}")

    seen = set()

    blocked_slugs = {
        "android",
        "apple",
        "brands",
        "accessories",
        "products",
        "home"
    }

    for name, slug, price in matches:

        try:

            name = str(name).strip()
            slug = str(slug).strip()
            price = str(price).strip()

            # Skip obvious non-products
            if name.lower() == "oliz store":
                continue

            if len(name) < 10:
                continue

            if slug.lower() in blocked_slugs:
                continue

            if name in seen:
                continue

            seen.add(name)

            products.append({
                "product_name": name,
                "price": f"Rs {price}",
                "marketplace": "Oliz",
                "search_term": "all-products",
                "link": f"https://olizstore.com/products/{slug}",
                "scraped_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            })

            if len(products) >= max_products:
                break

        except Exception:
            continue

    print(f"Found {len(products)} products")

    if products:
        print("\nSample Product:")
        print(products[0])

    return products


def save_to_csv(
    products,
    filename="data/raw/oliz_scraped.csv"
):

    if not products:
        print("No products found")
        return

    with open(
        filename,
        "w",
        newline="",
        encoding="utf-8"
    ) as f:

        writer = csv.DictWriter(
            f,
            fieldnames=products[0].keys()
        )

        writer.writeheader()
        writer.writerows(products)

    print(
        f"Saved {len(products)} products to {filename}"
    )


if __name__ == "__main__":

    products = scrape_oliz(max_products=200)

    save_to_csv(products)