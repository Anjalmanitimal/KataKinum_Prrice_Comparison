"""
SQLite-backed storage for the live application's data - the "Central
Database" stage of the project's Integration pipeline (products +
price history), as opposed to the offline scraping/cleaning/matching
pipeline in matcher/ and scraper/, which still produces CSVs as its
final output (matched_products.csv). That CSV is migrated into this
database via matcher/migrate_to_sqlite.py whenever it's regenerated.

Every function here returns/accepts plain pandas DataFrames, matching
the exact shape the rest of the backend already expects - so routes.py,
analytics.py and category_clustering.py don't need to know or care that
the data now lives in SQLite instead of a CSV file.
"""

import sqlite3
from pathlib import Path

import pandas as pd

DB_FILE = Path("data/processed/kata_kinum.db")

PRODUCTS_TABLE = "products"
PRICE_HISTORY_TABLE = "price_history"


def get_connection():
    DB_FILE.parent.mkdir(parents=True, exist_ok=True)
    return sqlite3.connect(DB_FILE, check_same_thread=False)


def load_products():
    with get_connection() as conn:
        return pd.read_sql(f"SELECT * FROM {PRODUCTS_TABLE}", conn)


def save_products(df):
    with get_connection() as conn:
        df.to_sql(PRODUCTS_TABLE, conn, if_exists="replace", index=False)


def load_price_history():
    with get_connection() as conn:
        try:
            return pd.read_sql(f"SELECT * FROM {PRICE_HISTORY_TABLE}", conn)
        except pd.errors.DatabaseError:
            return pd.DataFrame(columns=["product_id", "price_numeric", "recorded_at"])


def save_price_history(df):
    with get_connection() as conn:
        df.to_sql(PRICE_HISTORY_TABLE, conn, if_exists="replace", index=False)
