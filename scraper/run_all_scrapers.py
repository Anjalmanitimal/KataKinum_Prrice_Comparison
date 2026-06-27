import subprocess
import pandas as pd
import os

print("=" * 60)
print("KATA KINUM - RUNNING ALL SCRAPERS")
print("=" * 60)

# -------------------------
# Run Daraz Scraper
# -------------------------
print("\nRunning Daraz Scraper...")
subprocess.run(["python", "scraper/daraz_scraper.py"])

# -------------------------
# Run Hukut Scraper
# -------------------------
print("\nRunning Hukut Scraper...")
subprocess.run(["python", "scraper/hukut_scraper.py"])

# -------------------------
# Run Oliz Scraper
# -------------------------
print("\nRunning Oliz Scraper...")
subprocess.run(["python", "scraper/oliz_scraper.py"])

print("\nAll scrapers finished.")

print("\nLoading CSV files...")

daraz = pd.read_csv("data/raw/daraz_scraped.csv")
hukut = pd.read_csv("data/raw/hukut_scraped.csv")
oliz = pd.read_csv("data/raw/oliz_scraped.csv")

print(f"Daraz : {len(daraz)} products")
print(f"Hukut : {len(hukut)} products")
print(f"Oliz  : {len(oliz)} products")

combined = pd.concat(
    [
        daraz,
        hukut,
        oliz
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

print("\nCombined Dataset Created!")

print(f"Total Products : {len(combined)}")

print("\nSaved to:")
print("data/processed/combined_products.csv")

print("=" * 60)