import pandas as pd

recommendations = pd.read_csv(
    "data/processed/recommendations.csv"
)

matched = pd.read_csv(
    "data/processed/matched_products.csv"
)