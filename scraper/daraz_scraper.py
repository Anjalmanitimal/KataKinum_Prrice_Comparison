"""
Daraz Nepal Scraper
--------------------
Scrapes product name and price from Daraz Nepal.

Supports two modes:

1. Category Mode
   - Used to scrape default categories
   - Used for building the dataset

2. Search Mode
   - Used by Flask later
   - Example:
       scrape_daraz("iphone 16")
"""

import time
import csv

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from webdriver_manager.chrome import ChromeDriverManager


DEFAULT_CATEGORIES = [
    "smartphone",
    "laptop",
    "smartwatch",
    "earphone",
    "tablet"
]


def setup_driver():

    options = Options()

    options.add_argument("--headless=new")
    options.add_argument("--disable-gpu")
    options.add_argument("--window-size=1920,1080")

    options.add_argument(
        "user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64)"
    )

    driver = webdriver.Chrome(
        service=Service(
            ChromeDriverManager().install()
        ),
        options=options
    )

    return driver


def scrape_daraz(
    search_term=None,
    max_products=20
):

    if search_term is None:
        search_term = "smartphone"

    driver = setup_driver()

    url = (
        "https://www.daraz.com.np/catalog/?q="
        + search_term.replace(" ", "+")
    )

    print(f"Opening: {url}")

    driver.get(url)

    time.sleep(5)

    products = []

    try:

        items = driver.find_elements(
            By.CSS_SELECTOR,
            "[data-qa-locator='product-item']"
        )

        print(f"Found {len(items)} product cards")

        for item in items[:max_products]:

            name = "N/A"

            try:
                name = item.find_element(
                    By.CSS_SELECTOR,
                    "a[title]"
                ).get_attribute("title")
            except:
                pass

            if not name or name == "N/A":
                try:
                    name = item.find_element(
                        By.CSS_SELECTOR,
                        "img"
                    ).get_attribute("alt")
                except:
                    pass

            try:
                price = item.find_element(
                    By.CSS_SELECTOR,
                    ".currency--wrapper, .aBrP0"
                ).text
            except:
                price = "N/A"

            try:
                link = item.find_element(
                    By.TAG_NAME,
                    "a"
                ).get_attribute("href")
            except:
                link = "N/A"

            products.append({

                "product_name": name,
                "price": price,
                "marketplace": "Daraz",
                "search_term": search_term,
                "link": link

            })

    except Exception as e:

        print(e)

    driver.quit()

    return products


def scrape_default_categories(
    max_products=20
):

    all_products = []

    for category in DEFAULT_CATEGORIES:

        print(f"\nScraping {category}")

        products = scrape_daraz(

            search_term=category,
            max_products=max_products

        )

        all_products.extend(products)

        time.sleep(2)

    return all_products


def save_to_csv(
    products,
    filename="data/raw/daraz_scraped.csv"
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

    print("\nDaraz Scraper")

    print(
        f"Default categories: {', '.join(DEFAULT_CATEGORIES)}"
    )

    choice = input(
        "Press ENTER for defaults or type categories: "
    ).strip()

    if choice == "":

        return DEFAULT_CATEGORIES

    return [

        c.strip()

        for c in choice.split(",")

        if c.strip()

    ]


if __name__ == "__main__":

    categories = get_categories_from_user()

    print(
        f"\nWill scrape: {categories}"
    )

    all_products = []

    for category in categories:

        products = scrape_daraz(

            search_term=category,
            max_products=20

        )

        all_products.extend(products)

        time.sleep(2)

    print(
        f"\nTotal products: {len(all_products)}"
    )

    save_to_csv(all_products)