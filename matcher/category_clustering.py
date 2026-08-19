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

# Checked in this order (narrower/less ambiguous categories first) since
# some hint words aren't exclusive to one category - e.g. Samsung uses
# "galaxy" across phones, tablets, watches and earbuds alike, so "tab"/
# "watch"/"buds" must be checked before the generic "galaxy" catch-all.
TRUSTED_CATEGORY_HINTS = {
    "tablet": {"tablet", "ipad", "tab"},
    "smartwatch": {"smartwatch"},
    "earphone": {"earphone", "earbuds", "earbud", "airpods", "tws", "buds"},
    "laptop": {"laptop", "notebook", "macbook", "ultrabook", "chromebook"},
    "smartphone": {"iphone", "smartphone", "galaxy", "pixel", "redmi", "poco", "oneplus", "realme", "infinix", "tecno", "vivo", "oppo", "nothing"},
}


def guess_trusted_category(name):
    """Keyword fallback for rows whose search_term isn't a trusted
    category string - e.g. live search's search_term is the user's raw
    query, so it almost never equals "smartphone" etc. even when the
    result plainly is one. Without this, such rows would fall straight
    to the K-Means model below, which was fit only on the untagged
    general-catalog rows (bags/watches/cameras/powerbanks/audio/
    appliances) and has never seen a phone or laptop during training -
    it can only output one of those 6 labels, so it would confidently
    but wrongly bucket a phone into e.g. "bag". Heuristic, not
    guaranteed correct, but far more reliable than that for these
    common, recognizable cases.
    """

    words = set((name or "").lower().split())

    # "Galaxy Watch" and "Galaxy Buds" would otherwise fall through to the
    # generic "galaxy" -> smartphone catch-all below, since neither
    # contains the literal word "smartwatch" or a "buds"-prefixed word
    # together with "galaxy" specifically (as opposed to other brands'
    # earbuds, already caught by the earphone hints).
    if {"galaxy", "watch"} <= words:
        return "smartwatch"

    for category, hints in TRUSTED_CATEGORY_HINTS.items():
        if any(word.startswith(hint) for word in words for hint in hints):
            return category

    return None


NEW_CATEGORY_LABELS = {
    "bag": "Bags & Backpacks",
    "watch": "Watches",
    "camera_gear": "Drones & Camera Gear",
    "powerbank": "Power Banks & Chargers",
    "audio": "Speakers & Audio",
    "appliance": "Home Appliances",
}


def fit_categorizer(texts):
    """Fit the TF-IDF vectorizer + KMeans model once against the batch
    dataset, so later calls (e.g. categorizing a newly live-scraped
    product) can reuse this exact fitted model via categorize_names()
    instead of refitting - refitting would renumber the clusters and
    silently invalidate CLUSTER_LABELS, the same fragility documented
    above for matcher.product_matcher regenerating the dataset.
    """

    vectorizer = TfidfVectorizer(stop_words="english", max_features=400)
    vectors = vectorizer.fit_transform(texts)

    model = KMeans(n_clusters=N_CLUSTERS, random_state=RANDOM_STATE, n_init=10)
    model.fit(vectors)

    return vectorizer, model


def categorize_names(names, vectorizer, model):
    """Classify product names with an already-fitted vectorizer/model
    (see fit_categorizer) - uses .transform()/.predict(), never refits.
    """

    vectors = vectorizer.transform(names)
    cluster_ids = model.predict(vectors)

    return [CLUSTER_LABELS.get(c) for c in cluster_ids]


def auto_categorize(df, return_model=False):
    """Return a category label per row: the trusted search_term where
    available, otherwise a K-Means-discovered label, otherwise None.

    The K-Means fit itself is restricted to original batch rows (product
    IDs prefixed "P", assigned by matcher/product_matcher.py) - live
    search results (prefixed "L", see backend/routes.py) accumulate in
    the database indefinitely as people search, and must never join the
    fit pool, or the cluster boundaries - and therefore CLUSTER_LABELS,
    hand-tuned against the original batch composition - would silently
    drift further every time more live data piles up. Live rows still
    get categorized, just via categorize_names() against this same
    fitted model afterwards (see category_clustering.categorize_pending
    and backend/routes.py's assign_categories_to_new_rows), never by
    joining the fit itself.

    return_model=True also returns the fitted (vectorizer, model) so the
    caller can categorize other rows later via categorize_names()
    without refitting.
    """

    category = df["search_term"].where(
        df["search_term"].isin(TRUSTED_CATEGORIES),
        None
    )

    is_batch_row = df["product_id"].astype(str).str.startswith("P")
    untagged_mask = category.isna() & is_batch_row
    untagged = df[untagged_mask]

    if len(untagged) < N_CLUSTERS:
        return (category, None, None) if return_model else category

    texts = untagged["clean_name"].fillna("").astype(str).tolist()

    vectorizer, model = fit_categorizer(texts)

    discovered = categorize_names(texts, vectorizer, model)

    category.loc[untagged_mask] = discovered

    if return_model:
        return category, vectorizer, model

    return category


def categorize_pending(df, vectorizer, model):
    """Assign a category to every row still missing one after
    auto_categorize() - in practice, live-scraped rows (see the
    docstring above). Tries the keyword guess first, then falls back to
    the already-fitted K-Means model. Never refits.
    """

    category = df["category"].copy()
    unresolved_mask = category.isna()

    if not unresolved_mask.any():
        return category

    guessed = df.loc[unresolved_mask, "clean_name"].apply(guess_trusted_category)
    category.loc[unresolved_mask] = guessed

    unresolved_mask = category.isna()

    if unresolved_mask.any() and vectorizer is not None and model is not None:
        names = df.loc[unresolved_mask, "clean_name"].fillna("").astype(str).tolist()
        category.loc[unresolved_mask] = categorize_names(names, vectorizer, model)

    return category
