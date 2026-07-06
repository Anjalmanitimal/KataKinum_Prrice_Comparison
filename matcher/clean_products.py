import os
import re
import pandas as pd


INPUT_FILE = "data/processed/combined_products.csv"
OUTPUT_FILE = "data/processed/cleaned_products.csv"


# ----------------------------------------------------
# Clean Product Name
# ----------------------------------------------------
def clean_product_name(name):

    if pd.isna(name):
        return ""

    name = str(name).lower()

    # Remove common unnecessary words
    remove_words = [
        "official",
        "official warranty",
        "warranty",
        "price in nepal",
        "best price",
        "buy online",
        "buy",
        "online",
        "latest",
        "new",
        "offer",
        "discount",
        "available",
        "original",
        "genuine"
    ]

    for word in remove_words:
        name = name.replace(word, "")

    # Remove storage capacity
    name = re.sub(r"\b\d+\s?gb\b", "", name)
    name = re.sub(r"\b\d+\s?tb\b", "", name)

    # Remove RAM format (8+8 etc.)
    name = re.sub(r"\b\d+\+\d+\b", "", name)

    # Remove network labels
    name = re.sub(r"\b5g\b", "", name)
    name = re.sub(r"\b4g\b", "", name)

    # Remove text inside brackets
    name = re.sub(r"\(.*?\)", "", name)

    # Remove special characters
    name = re.sub(r"[^a-z0-9 ]", " ", name)

    # Remove multiple spaces
    name = re.sub(r"\s+", " ", name)

    return name.strip()


# ----------------------------------------------------
# Convert Price to Integer
# ----------------------------------------------------
def extract_price(price):

    if pd.isna(price):
        return None

    text = str(price)

    # Find prices like:
    # 1,46,599
    # 146599
    matches = re.findall(r"\d[\d,]*", text)

    if not matches:
        return None

    prices = []

    for match in matches:

        number = int(match.replace(",", ""))

        # Ignore tiny numbers like 16GB, 512GB, 2025 etc.
        if number >= 1000:
            prices.append(number)

    if not prices:
        return None

    # Usually the actual price is the largest number
    return max(prices)


# ----------------------------------------------------
# Main
# ----------------------------------------------------
def main():

    print("=" * 60)
    print("PRODUCT DATA CLEANING")
    print("=" * 60)

    if not os.path.exists(INPUT_FILE):
        print("Input file not found!")
        return

    df = pd.read_csv(INPUT_FILE)

    print(f"\nLoaded {len(df)} products")

    # Remove empty product names
    df = df[df["product_name"].notna()]

    # Remove empty prices
    df = df[df["price"].notna()]

    # Create clean name
    df["clean_name"] = df["product_name"].apply(clean_product_name)

    # Numeric price
    df["price_numeric"] = df["price"].apply(extract_price)

    # Remove rows where cleaning failed
    df = df[df["clean_name"] != ""]

    # Remove rows with invalid price
    df = df[df["price_numeric"].notna()]

    # Remove duplicates
    df.drop_duplicates(
        subset=["product_name", "marketplace"],
        inplace=True
    )

    # Sort alphabetically
    df.sort_values(
        by=["clean_name", "price_numeric"],
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

    print("\nCleaning Complete!")

    print(f"Products after cleaning : {len(df)}")

    print(f"\nSaved to\n{OUTPUT_FILE}")

    print("\nSample Data\n")

    print(
        df[
            [
                "product_name",
                "clean_name",
                "price",
                "price_numeric",
                "marketplace"
            ]
        ].head(15)
    )

    print("=" * 60)


if __name__ == "__main__":
    main()