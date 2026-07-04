import os
import pandas as pd

INPUT_FILE = "data/processed/matched_products.csv"
OUTPUT_FILE = "data/processed/recommendations.csv"


def main():

    print("=" * 60)
    print("RECOMMENDATION ENGINE")
    print("=" * 60)

    if not os.path.exists(INPUT_FILE):
        print("Matched products file not found.")
        return

    df = pd.read_csv(INPUT_FILE)

    print(f"\nLoaded {len(df)} matched products")

    recommendations = []

    grouped = df.groupby("product_id")

    for product_id, group in grouped:

        group = group.sort_values("price_numeric")

        cheapest = group.iloc[0]

        highest_price = group["price_numeric"].max()

        lowest_price = group["price_numeric"].min()

        average_price = round(group["price_numeric"].mean())

        savings = highest_price - lowest_price

        stores = ", ".join(sorted(group["marketplace"].unique()))

        recommendations.append({
            "product_id": product_id,
            "product_name": cheapest["product_name"],
            "clean_name": cheapest["clean_name"],
            "best_store": cheapest["marketplace"],
            "best_price": lowest_price,
            "highest_price": highest_price,
            "average_price": average_price,
            "savings": savings,
            "stores_available": len(group),
            "marketplaces": stores,
            "best_product_link": cheapest["link"]
        })

    recommendation_df = pd.DataFrame(recommendations)

    recommendation_df.sort_values(
        by="best_price",
        inplace=True
    )

    recommendation_df.to_csv(
        OUTPUT_FILE,
        index=False
    )

    print("\nRecommendation file created successfully!")

    print(f"Unique Products : {len(recommendation_df)}")

    print(f"\nSaved to\n{OUTPUT_FILE}")

    print("\nSample Recommendations:\n")

    print(
        recommendation_df[
            [
                "product_name",
                "best_store",
                "best_price",
                "highest_price",
                "savings"
            ]
        ].head(20)
    )

    print("=" * 60)


if __name__ == "__main__":
    main()