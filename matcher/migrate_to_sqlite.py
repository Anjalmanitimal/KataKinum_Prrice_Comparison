"""
One-time (and re-runnable) migration: loads matched_products.csv and
price_history.csv into the SQLite database backend/db.py reads from.

Run this whenever matched_products.csv is regenerated (e.g. after
re-running matcher/product_matcher.py), so the live application picks up
the latest data. price_history.csv is preserved as-is if it already
exists in the database - this only seeds it on a fresh database, it
never overwrites accumulated real tracking data.
"""

import os
import sys
from pathlib import Path

import pandas as pd

ROOT_DIR = Path(__file__).resolve().parent.parent
sys.path.append(str(ROOT_DIR))
os.chdir(ROOT_DIR)  # so relative "data/processed/..." paths resolve correctly

from backend.db import save_products, save_price_history, load_price_history


def migrate():
    matched = pd.read_csv("data/processed/matched_products.csv")
    save_products(matched)
    print(f"Migrated {len(matched)} product rows into the products table")

    existing_history = load_price_history()

    if len(existing_history) > 0:
        print(
            f"price_history table already has {len(existing_history)} rows - "
            "leaving it as-is (not overwriting real tracked data)"
        )
        return

    history_file = Path("data/processed/price_history.csv")

    if history_file.exists():
        history = pd.read_csv(history_file)
        save_price_history(history)
        print(f"Seeded price_history table with {len(history)} rows from CSV")
    else:
        print("No existing price_history.csv found - starting with an empty table")


if __name__ == "__main__":
    migrate()
