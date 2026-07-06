import pandas as pd
import os

from scraper.daraz_scraper import scrape_daraz
from scraper.hukut_scraper import scrape_hukut
from scraper.oliz_scraper import scrape_oliz

from matcher.clean_products import main as clean_products
from matcher.product_matcher import main as match_products
from matcher.recommendation_engine import main as recommendation_engine


DEFAULT_PRODUCTS = [
    "smartphone",
    "laptop",
    "smartwatch",
    "earphone",
    "tablet"
]

def build_dataset():

    print("=" * 60)
    print("BUILDING DATASET")
    print("=" * 60)

    # ---------------------------------------
    # DARAZ
    # ---------------------------------------
    print("\nScraping Daraz...")

    daraz_products = []

    for product in DEFAULT_PRODUCTS:

        print(f"  {product}")

        daraz_products.extend(
            scrape_daraz(
                search_term=product,
                max_products=20
            )
        )

    pd.DataFrame(daraz_products).to_csv(
        "data/raw/daraz_scraped.csv",
        index=False
    )

    print(f"Daraz : {len(daraz_products)} products")

    # ---------------------------------------
    # HUKUT
    # ---------------------------------------
    print("\nScraping Hukut...")

    hukut_products = []

    for product in DEFAULT_PRODUCTS:

        print(f"  {product}")

        hukut_products.extend(
            scrape_hukut(
                search_term=product,
                max_products=20
            )
        )

    pd.DataFrame(hukut_products).to_csv(
        "data/raw/hukut_scraped.csv",
        index=False
    )

    print(f"Hukut : {len(hukut_products)} products")

    # ---------------------------------------
    # OLIZ
    # ---------------------------------------
    print("\nScraping Oliz...")

    oliz_products = scrape_oliz(
        search_term=None,
        max_products=200
    )

    pd.DataFrame(oliz_products).to_csv(
        "data/raw/oliz_scraped.csv",
        index=False
    )

    print(f"Oliz : {len(oliz_products)} products")

        # ---------------------------------------
    # COMBINE ALL PRODUCTS
    # ---------------------------------------

    print("\nCombining datasets...")

    combined = pd.concat(
        [
            pd.DataFrame(daraz_products),
            pd.DataFrame(hukut_products),
            pd.DataFrame(oliz_products)
        ],
        ignore_index=True
    )

    combined.drop_duplicates(
        subset=["product_name", "marketplace"],
        inplace=True
    )

    os.makedirs(
        "data/processed",
        exist_ok=True
    )

    combined.to_csv(
        "data/processed/combined_products.csv",
        index=False
    )

    print(f"Combined : {len(combined)} products")

    # ---------------------------------------
    # RUN PIPELINE
    # ---------------------------------------

    print("\nCleaning products...")
    clean_products()

    print("\nMatching products...")
    match_products()

    print("\nGenerating recommendations...")
    recommendation_engine()

    print("\n" + "=" * 60)
    print("DATASET BUILD COMPLETE")
    print("=" * 60)

    print("\nFiles created:")

    print("✓ data/raw/daraz_scraped.csv")
    print("✓ data/raw/hukut_scraped.csv")
    print("✓ data/raw/oliz_scraped.csv")
    print("✓ data/processed/combined_products.csv")
    print("✓ data/processed/cleaned_products.csv")
    print("✓ data/processed/matched_products.csv")
    print("✓ data/processed/recommendations.csv")


if __name__ == "__main__":
    build_dataset()