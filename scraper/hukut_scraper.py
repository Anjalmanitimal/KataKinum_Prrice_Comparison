"""
Hukut Nepal Scraper
---------------------
Scrapes product name, price, and link from Hukut.com category pages.
"""

import time
import csv
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
from datetime import datetime


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

    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=options)

    return driver


def scrape_hukut(search_term, max_products=20):

    driver = setup_driver()

    slug = CATEGORY_URL_MAP.get(
        search_term.lower(),
        search_term.replace(" ", "-")
    )

    url = f"https://hukut.com/{slug}"

    print(f"Opening: {url}")

    driver.get(url)

    time.sleep(8)

    products = []

    try:

        # Save page for debugging
        with open("hukut_debug.html", "w", encoding="utf-8") as f:
            f.write(driver.page_source)

        print("Saved page HTML")

        cards = driver.find_elements(By.CSS_SELECTOR, "h3[title]")

        print(f"Found {len(cards)} potential products")

        seen = set()

        for card in cards:

            try:
                name = card.get_attribute("title").strip()

                if not name:
                    continue

                if name in seen:
                    continue

                seen.add(name)

                # Find nearest product link
                link = "N/A"

                try:
                    parent_link = card.find_element(
                        By.XPATH,
                        "./ancestor::a[1]"
                    )

                    link = parent_link.get_attribute("href")

                except Exception:
                    pass

                # Try to locate price
                price = "N/A"

                try:
                    container = card.find_element(
                        By.XPATH,
                        "./ancestor::*[self::div or self::article][1]"
                    )

                    text = container.text.split("\n")

                    for line in text:

                        line = line.strip()

                        if (
                            "Rs" in line
                            or "रु" in line
                            or "," in line
                        ):
                            price = line
                            break

                except Exception:
                    pass

                products.append({
                    "product_name": name,
                    "price": price,
                    "marketplace": "Hukut",
                    "search_term": search_term,
                    "link": link
                })

                if len(products) >= max_products:
                    break

            except Exception:
                continue

    except Exception as e:
        print("Scraping error:", e)

    driver.quit()

    return products


def save_to_csv(products,
                filename="data/raw/hukut_scraped.csv"):

    if not products:
        print("No products found.")
        return

    keys = products[0].keys()

    with open(
        filename,
        "w",
        newline="",
        encoding="utf-8"
    ) as f:

        writer = csv.DictWriter(
            f,
            fieldnames=keys
        )

        writer.writeheader()
        writer.writerows(products)

    print(
        f"Saved {len(products)} products to {filename}"
    )


def get_categories_from_user():

    print("\n--- Hukut Scraper ---")
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
        f"\nWill scrape these categories: {categories}"
    )

    all_products = []

    for category in categories:

        print(
            f"\n--- Scraping category: {category} ---"
        )

        products = scrape_hukut(
            category,
            max_products=20
        )

        all_products.extend(products)

        time.sleep(3)

    print(
        f"\nTotal products scraped: {len(all_products)}"
    )

    save_to_csv(all_products)
    "scraped_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S")