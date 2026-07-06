"""
Hukut Nepal Scraper
-------------------
Supports two modes:

1. Dataset Mode (default)
   - mobile-phones
   - laptops
   - smartwatches
   - earbuds
   - tablets

2. Live Search Mode
   Example:
   iphone 16
   samsung s25 ultra
   macbook air m4
"""

import time
import csv
from datetime import datetime

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from webdriver_manager.chrome import ChromeDriverManager


DEFAULT_CATEGORIES = [
    "mobile-phones",
    "laptops",
    "smartwatches",
    "earbuds",
    "tablets"
]


CATEGORY_URL_MAP = {
    "smartphone": "mobile-phones",
    "mobile-phones": "mobile-phones",

    "laptop": "laptops",
    "laptops": "laptops",

    "smartwatch": "smartwatches",
    "smartwatches": "smartwatches",

    "earphone": "earbuds",
    "earbuds": "earbuds",

    "tablet": "tablets",
    "tablets": "tablets",
}


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


def scrape_hukut(
        search_term,
        max_products=20,
        live_search=False
):

    driver = setup_driver()

    if live_search:

        url = (
            "https://hukut.com/search?q="
            + search_term.replace(" ", "+")
        )

    else:

        slug = CATEGORY_URL_MAP.get(
            search_term.lower(),
            search_term.replace(" ", "-")
        )

        url = f"https://hukut.com/{slug}"

    print(f"Opening: {url}")

    driver.get(url)

    time.sleep(8)

    with open(
        "hukut_debug.html",
        "w",
        encoding="utf-8"
    ) as f:
        f.write(driver.page_source)

    print("Saved page HTML")

    cards = driver.find_elements(
        By.CSS_SELECTOR,
        "h3[title]"
    )

    print(f"Found {len(cards)} potential products")

    products = []
    seen = set()

    for card in cards:

        try:

            name = card.get_attribute("title").strip()

            if not name:
                continue

            if name in seen:
                continue

            seen.add(name)

            # -----------------------
            # Product Link
            # -----------------------

            link = "N/A"

            try:

                parent = card.find_element(
                    By.XPATH,
                    "./ancestor::a[1]"
                )

                link = parent.get_attribute("href")

            except Exception:
                pass

            # -----------------------
            # Product Price
            # -----------------------

            price = "N/A"
            try:

                product_card = card.find_element(
                    By.XPATH,
                    "./ancestor::div[contains(@class,'flex-col')][1]"
                )
                prices = product_card.find_elements(
                    By.XPATH,
                    ".//span[contains(text(),'Rs')]"
                 )

                if prices:
                    price = prices[0].text.strip()

            except Exception:
             pass

            products.append({

                "product_name": name,

                "price": price,

                "marketplace": "Hukut",

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

    driver.quit()

    return products


def save_to_csv(
        products,
        filename="data/raw/hukut_scraped.csv"
):

    if not products:
        print("No products found.")
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

    print(f"Saved {len(products)} products")


def get_categories_from_user():

    print("\nHukut Scraper")
    print(
        "Default categories: "
        + ", ".join(DEFAULT_CATEGORIES)
    )

    choice = input(
        "\nPress ENTER for defaults or type product/category: "
    ).strip()

    if choice == "":

        return DEFAULT_CATEGORIES, False

    return [choice], True


if __name__ == "__main__":

    categories, live_mode = get_categories_from_user()

    print()

    if live_mode:
        print("Running in LIVE SEARCH mode")
    else:
        print("Running in DATASET mode")

    all_products = []

    for category in categories:

        print(f"\nScraping: {category}")

        products = scrape_hukut(
            category,
            max_products=20,
            live_search=live_mode
        )

        all_products.extend(products)

        time.sleep(2)

    print()

    print(f"Total products: {len(all_products)}")

    save_to_csv(all_products)