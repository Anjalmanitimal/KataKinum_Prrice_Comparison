import os
import pandas as pd

from scraper.daraz_scraper import scrape_daraz
from scraper.hukut_scraper import scrape_hukut
from scraper.oliz_scraper import scrape_oliz

from matcher.clean_products import main as clean_products
from matcher.product_matcher import main as match_products
from matcher.recommendation_engine import main as recommend_products


RAW_FOLDER = "data/raw"
PROCESSED_FOLDER = "data/processed"


os.makedirs(RAW_FOLDER, exist_ok=True)
os.makedirs(PROCESSED_FOLDER, exist_ok=True)


def combine_csvs():

    print("\nLoading scraped CSV files...")

    daraz = pd.read_csv(
        "data/raw/daraz_scraped.csv"
    )

    hukut = pd.read_csv(
        "data/raw/hukut_scraped.csv"
    )

    oliz = pd.read_csv(
        "data/raw/oliz_scraped.csv"
    )

    print(f"Daraz : {len(daraz)}")
    print(f"Hukut : {len(hukut)}")
    print(f"Oliz  : {len(oliz)}")

    combined = pd.concat(
        [
            daraz,
            hukut,
            oliz
        ],
        ignore_index=True
    )

    combined.drop_duplicates(
        subset=[
            "product_name",
            "marketplace"
        ],
        inplace=True
    )

    combined.to_csv(
        "data/processed/combined_products.csv",
        index=False
    )

    print("\nCombined products :", len(combined))
    def run_dataset_mode():

        print("\n" + "=" * 60)
    print("RUNNING DATASET MODE")
    print("=" * 60)

    categories = [
        "smartphone",
        "laptop",
        "smartwatch",
        "earphone",
        "tablet"
    ]

    # -----------------------------
    # Daraz
    # -----------------------------
    print("\nScraping Daraz...")

    daraz_products = []

    for category in categories:

        print(f"  {category}")

        daraz_products.extend(
            scrape_daraz(
                search_term=category,
                max_products=20
            )
        )

    pd.DataFrame(
        daraz_products
    ).to_csv(
        "data/raw/daraz_scraped.csv",
        index=False
    )

    # -----------------------------
    # Hukut
    # -----------------------------
    print("\nScraping Hukut...")

    hukut_products = []

    for category in categories:

        print(f"  {category}")

        hukut_products.extend(
            scrape_hukut(
                search_term=category,
                max_products=20
            )
        )

    pd.DataFrame(
        hukut_products
    ).to_csv(
        "data/raw/hukut_scraped.csv",
        index=False
    )

    # -----------------------------
    # Oliz
    # -----------------------------
    print("\nScraping Oliz...")

    oliz_products = scrape_oliz(
        search_term=None,
        max_products=200
    )

    pd.DataFrame(
        oliz_products
    ).to_csv(
        "data/raw/oliz_scraped.csv",
        index=False
    )

    combine_csvs()

    clean_products()

    match_products()

    generate_recommendations()

    print("\nDataset Pipeline Complete!")


def run_live_search():

    print("\n" + "=" * 60)
    print("LIVE SEARCH MODE")
    print("=" * 60)

    search = input(
        "\nEnter product name: "
    ).strip()

    if search == "":
        print("No search entered.")
        return

    print("\nSearching Daraz...")

    daraz = scrape_daraz(
        search_term=search,
        max_products=20
    )

    pd.DataFrame(
        daraz
    ).to_csv(
        "data/raw/daraz_scraped.csv",
        index=False
    )

    print("\nSearching Hukut...")

    hukut = scrape_hukut(
        search_term=search,
        max_products=20
    )

    pd.DataFrame(
        hukut
    ).to_csv(
        "data/raw/hukut_scraped.csv",
        index=False
    )

    print("\nSearching Oliz...")

    oliz = scrape_oliz(
        search_term=search,
        max_products=50
    )

    pd.DataFrame(
        oliz
    ).to_csv(
        "data/raw/oliz_scraped.csv",
        index=False
    )

    combine_csvs()

    clean_products()

    match_products()

    generate_recommendations()

    print("\nLive Search Pipeline Complete!")


if __name__ == "__main__":

    print("=" * 60)
    print("KATA KINUM SEARCH PIPELINE")
    print("=" * 60)

    print("\n1. Dataset Mode")
    print("2. Live Search Mode")

    choice = input("\nChoose (1/2): ").strip()

    if choice == "1":

        run_dataset_mode()

    elif choice == "2":

        run_live_search()

    else:

        print("Invalid choice.")