import os
import re
import pandas as pd
from rapidfuzz import fuzz

INPUT_FILE = "data/processed/cleaned_products.csv"
OUTPUT_FILE = "data/processed/matched_products.csv"

SIMILARITY_THRESHOLD = 85


# ----------------------------------------------------
# Create a base model name
# ----------------------------------------------------
def normalize_model(name):

    name = str(name).lower()

    # remove brackets
    name = re.sub(r"\(.*?\)", "", name)

    # remove storage
    name = re.sub(r"\b\d+\s?gb\b", "", name)
    name = re.sub(r"\b\d+\s?tb\b", "", name)

    # remove RAM
    name = re.sub(r"\b\d+\s?ram\b", "", name)

    # remove processor words
    remove_words = [
        "intel",
        "amd",
        "ryzen",
        "core",
        "graphics",
        "processor",
        "ssd",
        "hdd",
        "display",
        "ips",
        "oled",
        "wuxga",
        "fhd",
        "uhd",
        "touch",
        "backlit",
        "keyboard",
        "windows",
        "win",
        "warranty"
    ]

    for word in remove_words:
        name = re.sub(rf"\b{word}\b", "", name)

    name = re.sub(r"[^a-z0-9 ]", " ", name)
    name = re.sub(r"\s+", " ", name)

    return name.strip()


# ----------------------------------------------------
# Assign Product IDs
# ----------------------------------------------------
def assign_product_groups(df):

    product_ids = []

    known = []

    counter = 1

    for _, row in df.iterrows():

        current = normalize_model(row["clean_name"])

        found = False

        for product in known:

            similarity = fuzz.token_sort_ratio(
                current,
                product["name"]
            )

            if similarity >= SIMILARITY_THRESHOLD:

                product_ids.append(product["id"])
                found = True
                break

        if not found:

            pid = f"P{counter:04d}"

            known.append({
                "id": pid,
                "name": current
            })

            product_ids.append(pid)

            counter += 1

    return product_ids


# ----------------------------------------------------
# Main
# ----------------------------------------------------
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

    os.makedirs(
        "data/processed",
        exist_ok=True
    )

    df.to_csv(
        OUTPUT_FILE,
        index=False
    )

    print("\nMatching Complete!")

    print(f"Matched products : {len(df)}")
    print(f"Unique Products : {df['product_id'].nunique()}")

    print(f"\nSaved to\n{OUTPUT_FILE}")

    print("\nSample\n")

    print(
        df[
            [
                "product_id",
                "product_name",
                "marketplace",
                "price_numeric"
            ]
        ].head(20)
    )

    print("=" * 60)


if __name__ == "__main__":
    main()