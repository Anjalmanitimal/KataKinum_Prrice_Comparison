import os
import pandas as pd
from rapidfuzz import fuzz

INPUT_FILE = "data/processed/cleaned_products.csv"
OUTPUT_FILE = "data/processed/matched_products.csv"

SIMILARITY_THRESHOLD = 90


def assign_product_groups(df):

    product_groups = []
    known_products = []

    group_counter = 1

    for clean_name in df["clean_name"]:

        matched = False

        for group in known_products:

            similarity = fuzz.token_sort_ratio(
                clean_name,
                group["clean_name"]
            )

            if similarity >= SIMILARITY_THRESHOLD:

                product_groups.append(group["product_id"])
                matched = True
                break

        if not matched:

            product_id = f"P{group_counter:04d}"

            known_products.append({
                "product_id": product_id,
                "clean_name": clean_name
            })

            product_groups.append(product_id)

            group_counter += 1

    return product_groups


def main():

    print("=" * 60)
    print("PRODUCT MATCHING")
    print("=" * 60)

    if not os.path.exists(INPUT_FILE):
        print("Input file not found.")
        return

    df = pd.read_csv(INPUT_FILE)

    print(f"\nLoaded {len(df)} cleaned products")

    df["product_id"] = assign_product_groups(df)

    df.sort_values(
        by=[
            "product_id",
            "price_numeric"
        ],
        inplace=True
    )

    df.to_csv(
        OUTPUT_FILE,
        index=False
    )

    print("\nMatching Complete!")

    print(f"Matched products : {len(df)}")

    print(
        f"Unique Products : {df['product_id'].nunique()}"
    )

    print(f"\nSaved to\n{OUTPUT_FILE}")

    print("\nSample:\n")

    print(
        df[
            [
                "product_id",
                "clean_name",
                "marketplace",
                "price_numeric"
            ]
        ].head(20)
    )

    print("=" * 60)


if __name__ == "__main__":
    main()