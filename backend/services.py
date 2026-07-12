import sys
from pathlib import Path

import pandas as pd

ROOT_DIR = Path(__file__).resolve().parent.parent
sys.path.append(str(ROOT_DIR))
from matcher.category_clustering import auto_categorize

recommendations = pd.read_csv(
    "data/processed/recommendations.csv"
)

matched = pd.read_csv(
    "data/processed/matched_products.csv"
)

matched["category"] = auto_categorize(matched)