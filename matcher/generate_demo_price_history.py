"""
Generates clearly-labeled SIMULATED price history, for demo purposes only.

Real price tracking (backend/price_history.py) only has a couple of days
of genuine data at any point early in the project's life - not enough to
show a meaningful trend chart. Waiting weeks for real data to accumulate
isn't practical for a student project on a deadline, so this generates a
synthetic multi-week price history instead, to demonstrate what the trend
visualization looks like once real data exists.

This is written to a SEPARATE file (price_history_demo.csv), never merged
into the real price_history.csv, and is only ever read by one clearly
labeled aggregate chart (analytics.py: price_trend_overview_chart). It
must never feed a per-product "buy now or wait" recommendation shown to
someone making an actual purchase decision - that stays real-data-only.

Each product's simulated walk ends AT its real current price (so the
"today" price shown anywhere else in the app stays accurate) and works
backward with small random weekly changes to build a plausible history.
"""

import random

import pandas as pd

OUTPUT_FILE = "data/processed/price_history_demo.csv"
WEEKS = 6
WEEKLY_CHANGE_RANGE = (-0.05, 0.05)  # up to +/-5% per simulated week

random.seed(42)


def generate(matched_path="data/processed/matched_products.csv"):
    matched = pd.read_csv(matched_path)

    priced = matched.dropna(subset=["price_numeric", "product_id"])
    current_price = priced.groupby("product_id")["price_numeric"].min()

    rows = []

    for product_id, today_price in current_price.items():
        price = float(today_price)
        weekly_prices = [price]

        # walk backward from today's real price to build a plausible past
        for _ in range(WEEKS - 1):
            change = random.uniform(*WEEKLY_CHANGE_RANGE)
            price = price / (1 + change)
            weekly_prices.append(round(price, 2))

        weekly_prices.reverse()  # oldest first

        for week_index, price in enumerate(weekly_prices):
            days_ago = (WEEKS - 1 - week_index) * 7
            date = pd.Timestamp.now(tz="UTC").normalize() - pd.Timedelta(days=days_ago)

            rows.append({
                "product_id": product_id,
                "price_numeric": price,
                "recorded_at": date.date().isoformat(),
            })

    df = pd.DataFrame(rows)
    df.to_csv(OUTPUT_FILE, index=False)

    return df


if __name__ == "__main__":
    df = generate()
    print(f"Generated {len(df)} simulated price points for {df['product_id'].nunique()} products")
    print(f"Saved to {OUTPUT_FILE}")
