"""
Auto-categorization for products that don't already have a trusted category.

Daraz and Hukut's own category listings ("smartphone", "laptop", "tablet",
"smartwatch", "earphone") are used as ground truth wherever available - they
came directly from the marketplaces' own taxonomy, so they're trusted as-is.

Everything else (mostly Oliz's general catalog scrape, tagged "all-products")
has no category at all. Rather than leaving that half of the dataset
unbrowsable, K-Means clustering is run on TF-IDF vectors of the untagged
product names to discover natural groupings, which are then labeled by hand
after inspecting each cluster's centroid terms and sample products - standard
practice for interpreting unsupervised clusters.

K=15 and the CLUSTER_LABELS mapping below were chosen by exploring the actual
dataset (see conversation/report for the cluster inspection output). Because
KMeans(random_state=...) is deterministic for a *fixed* dataset, this mapping
reproduces the same clusters each run against that same data - but cluster
ID numbering is NOT stable across changes to the underlying rows: K-Means'
initialization and the resulting cluster order depend on row order/content,
so re-running `matcher/product_matcher.py` (which re-sorts and re-numbers
`matched_products.csv`) shuffles which numeric cluster ID means what. This
mapping must be re-inspected and rebuilt after any change that touches which
rows exist or their order - already learned the hard way once when a matcher
fix silently invalidated this mapping (cluster "8" stopped meaning "audio").
"""

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.cluster import KMeans

TRUSTED_CATEGORIES = {"smartphone", "laptop", "tablet", "smartwatch", "earphone"}

N_CLUSTERS = 15
RANDOM_STATE = 42

# cluster id -> discovered category, hand-labeled after inspecting each
# cluster's top TF-IDF terms and sample product names
CLUSTER_LABELS = {
    1: "bag", 5: "bag", 8: "bag", 10: "bag",          # Aoking laptop bags/backpacks
    3: "watch", 11: "watch", 14: "watch",             # Seiko / Citizen / Tissot watches
    2: "camera_gear", 4: "camera_gear", 7: "camera_gear",
    9: "camera_gear", 13: "camera_gear",              # DJI drones/mics + K&F Concept mounts/cases
    0: "powerbank",                                   # Adam Elements power banks
    12: "audio",                                      # JBL / Marshall / Harman Kardon speakers
    6: "appliance",                                   # Dyson purifiers/hair dryers
}

NEW_CATEGORY_LABELS = {
    "bag": "Bags & Backpacks",
    "watch": "Watches",
    "camera_gear": "Drones & Camera Gear",
    "powerbank": "Power Banks & Chargers",
    "audio": "Speakers & Audio",
    "appliance": "Home Appliances",
}


def auto_categorize(df):
    """Return a category label per row: the trusted search_term where
    available, otherwise a K-Means-discovered label, otherwise None.
    """

    category = df["search_term"].where(
        df["search_term"].isin(TRUSTED_CATEGORIES),
        None
    )

    untagged_mask = category.isna()
    untagged = df[untagged_mask]

    if len(untagged) < N_CLUSTERS:
        return category

    texts = untagged["clean_name"].fillna("").astype(str).tolist()

    vectorizer = TfidfVectorizer(stop_words="english", max_features=400)
    vectors = vectorizer.fit_transform(texts)

    model = KMeans(n_clusters=N_CLUSTERS, random_state=RANDOM_STATE, n_init=10)
    cluster_ids = model.fit_predict(vectors)

    discovered = [CLUSTER_LABELS.get(c) for c in cluster_ids]

    category.loc[untagged_mask] = discovered

    return category
