import sys
from pathlib import Path

import pandas as pd

ROOT_DIR = Path(__file__).resolve().parent.parent
sys.path.append(str(ROOT_DIR))
from matcher.category_clustering import auto_categorize
from db import load_products

recommendations = pd.read_csv(
    "data/processed/recommendations.csv"
)

matched = load_products()

matched["category"] = auto_categorize(matched)