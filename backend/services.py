import sys
from pathlib import Path

import pandas as pd

ROOT_DIR = Path(__file__).resolve().parent.parent
sys.path.append(str(ROOT_DIR))
from matcher.category_clustering import auto_categorize, categorize_pending
from db import load_products

recommendations = pd.read_csv(
    "data/processed/recommendations.csv"
)

matched = load_products()

matched["category"], category_vectorizer, category_model = auto_categorize(
    matched, return_model=True
)

# Covers live-scraped rows persisted in an earlier server run - their
# category never joins the K-Means fit above (see auto_categorize), so
# they'd otherwise stay uncategorized (and invisible under Categories
# browsing) forever after a restart.
matched["category"] = categorize_pending(matched, category_vectorizer, category_model)