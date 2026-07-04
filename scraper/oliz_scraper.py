"""
Oliz Store Scraper
------------------
Supports two modes.

1. DATASET MODE
   - Scrapes entire product catalogue

2. LIVE SEARCH MODE
   - Searches products entered by the user
"""

import time
import csv
import re
from datetime import datetime

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager


DEFAULT_CATEGORY_URL = "https://olizstore.com/products"


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


def scrape_oliz(
        search_term=None,
        max_products=200
):

    driver = setup_driver()

    if search_term:

        url = (
            "https://olizstore.com/search?q="
            + search_term.replace(" ", "+")
        )

        print("\nRunning in LIVE SEARCH mode")

    else:

        url = DEFAULT_CATEGORY_URL

        print("\nRunning in DATASET mode")

    print(f"Opening: {url}")

    driver.get(url)

    time.sleep(8)

    with open(
        "oliz_debug.html",
        "w",
        encoding="utf-8"
    ) as f:

        f.write(driver.page_source)

    print("Saved page source")

    products = []

    seen = set()

 # ==================================================
    # LIVE SEARCH MODE
    # ==================================================
    if search_term:

        cards = driver.find_elements(
            By.CSS_SELECTOR,
            "a[href*='/product/']"
        )

        print(f"Found {len(cards)} possible product cards")

        for card in cards:

            try:

                link = card.get_attribute("href")

                if not link:
                    continue

                if link.startswith("/"):
                    link = "https://olizstore.com" + link

                # -----------------------------
                # Product Name
                # -----------------------------
                name = ""

                try:
                    name = card.find_element(
                        By.CSS_SELECTOR,
                        ".product-title"
                    ).text.strip()
                except:
                    pass

                if not name:

                    try:
                        name = card.text.split("\n")[0].strip()
                    except:
                        continue

                if not name:
                    continue

                # -----------------------------
                # Price
                # -----------------------------
                price = "N/A"

                try:

                    price = card.find_element(
                        By.CSS_SELECTOR,
                        ".product-price"
                    ).text.strip()

                    if price:
                        price = "Rs " + price

                except:
                    pass

                if name in seen:
                    continue

                seen.add(name)

                products.append({

                    "product_name": name,

                    "price": price,

                    "marketplace": "Oliz",

                    "search_term": search_term,

                    "link": link,

                    "scraped_at": datetime.now().strftime(
                        "%Y-%m-%d %H:%M:%S"
                    )

                })

                if len(products) >= max_products:
                    break

            except Exception:
                continue

    # ==================================================
    # DATASET MODE
    # ==================================================
    else:

        page = driver.page_source

        pattern = r'"name":"([^"]+)".*?"slug":"([^"]+)".*?"price":(\d+)'

        matches = re.findall(
            pattern,
            page,
            re.DOTALL
        )

        print(f"Raw matches found: {len(matches)}")

        blocked_slugs = {
            "android",
            "apple",
            "brands",
            "products",
            "accessories",
            "home"
        }

        for name, slug, price in matches:

            try:

                name = name.strip()
                slug = slug.strip()
                price = price.strip()

                if name.lower() == "oliz store":
                    continue

                if len(name) < 8:
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

                    "scraped_at": datetime.now().strftime(
                        "%Y-%m-%d %H:%M:%S"
                    )

                })

                if len(products) >= max_products:
                    break

            except Exception:
                continue
                driver.quit()

    print(f"Found {len(products)} products")

    if products:

        print("\nSample Product\n")

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

    print(f"\nSaved {len(products)} products")


if __name__ == "__main__":

    print("\nOliz Scraper")

    choice = input(
        "\nPress ENTER for dataset mode or type product name: "
    ).strip()

    if choice == "":

        products = scrape_oliz(
            search_term=None,
            max_products=200
        )

    else:

        products = scrape_oliz(
            search_term=choice,
            max_products=50
        )

    print(f"\nTotal products: {len(products)}")

    save_to_csv(products)