import sys
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor

ROOT_DIR = Path(__file__).resolve().parent.parent
sys.path.append(str(ROOT_DIR))
from scraper.daraz_scraper import scrape_daraz
from scraper.hukut_scraper import scrape_hukut
from scraper.oliz_scraper import scrape_oliz
from matcher.clean_products import clean_product_name, extract_price
from rapidfuzz import fuzz
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import pandas as pd
from flask import Blueprint
from flask import jsonify
from flask import request

from services import recommendations
from services import matched

api = Blueprint("api", __name__)

SCRAPE_TIMEOUT_SECONDS = 30

ACCESSORY_WORDS = [
    "case",
    "cover",
    "tempered",
    "glass",
    "charger",
    "cable",
    "protector",
    "earbuds",
    "earphone",
    "headphone",
    "adapter",
    "skin",
    "screen guard",
    "back cover",
    "pouch",
    "holder",
    "strap",
    "stand",
]


def filter_and_rank(products, query):
    words = [w for w in query.lower().split() if w]

    ranked = []
    for product in products:
        name = (product.get("product_name") or "").lower()

        if any(word in name for word in ACCESSORY_WORDS):
            continue

        score = sum(1 for word in words if word in name)
        ranked.append((score, product))

    ranked.sort(key=lambda item: item[0], reverse=True)

    return [product for score, product in ranked]


_live_id_counter = 0
_LIVE_MATCH_THRESHOLD = 85


def assign_live_product_ids(products):
    global _live_id_counter

    known = []

    for product in products:

        clean_name = clean_product_name(product.get("product_name", ""))
        price_numeric = extract_price(product.get("price"))

        product["clean_name"] = clean_name
        product["price_numeric"] = price_numeric

        matched_id = None

        for entry in known:
            similarity = fuzz.token_sort_ratio(clean_name, entry["name"])
            if similarity >= _LIVE_MATCH_THRESHOLD:
                matched_id = entry["id"]
                break

        if matched_id is None:
            _live_id_counter += 1
            matched_id = f"L{_live_id_counter:04d}"
            known.append({"id": matched_id, "name": clean_name})

        product["product_id"] = matched_id

    return products


def group_by_product(records):
    groups = {}
    order = []

    for row in records:
        pid = row.get("product_id")
        relevance = row.get("relevance_score") or 0

        if pid not in groups:
            groups[pid] = {
                "product_id": pid,
                "product_name": row.get("product_name"),
                "clean_name": row.get("clean_name"),
                "offers": [],
                "relevance_score": relevance,
            }
            order.append(pid)
        else:
            groups[pid]["relevance_score"] = max(
                groups[pid]["relevance_score"],
                relevance
            )

        groups[pid]["offers"].append({
            "marketplace": row.get("marketplace"),
            "price": row.get("price"),
            "price_numeric": row.get("price_numeric"),
            "link": row.get("link"),
        })

    grouped = []

    for pid in order:
        group = groups[pid]

        group["offers"].sort(
            key=lambda o: (
                o["price_numeric"] is None,
                o["price_numeric"]
            )
        )

        best = group["offers"][0]
        group["lowest_price"] = best["price_numeric"]
        group["lowest_price_display"] = best["price"]
        group["store_count"] = len(group["offers"])

        grouped.append(group)

    return grouped


SEMANTIC_MIN_SCORE = 0.15


def semantic_match(query, df, text_column="clean_name", top_k=40):
    """TF-IDF + cosine similarity search, layered on top of exact matching.

    Finds products related to the query in meaning/wording even when the
    query isn't a literal substring of the product name (e.g. word order
    differs, or the query only shares some words with the name).
    """

    if not query.strip() or len(df) == 0:
        return df.iloc[0:0].copy()

    texts = df[text_column].fillna("").astype(str).tolist()

    vectorizer = TfidfVectorizer(stop_words="english")

    try:
        tfidf_matrix = vectorizer.fit_transform(texts + [query])
    except ValueError:
        return df.iloc[0:0].copy()

    scores = cosine_similarity(
        tfidf_matrix[-1],
        tfidf_matrix[:-1]
    ).flatten()

    scored = df.copy()
    scored["relevance_score"] = scores

    scored = scored[scored["relevance_score"] >= SEMANTIC_MIN_SCORE]
    scored = scored.sort_values("relevance_score", ascending=False)

    return scored.head(top_k)


@api.route("/")
def home():

    return jsonify({
        "message": "Kata Kinum API Running"
    })


@api.route("/search")
def search():

    global matched

    q = request.args.get("q", "").lower().strip()

    if q == "":
        return jsonify([])

    # =========================
    # Search existing dataset
    # (exact substring match + semantic/TF-IDF match, combined)
    # =========================

    exact_result = matched[
        matched["product_name"]
        .str.lower()
        .str.contains(q, na=False)
    ].copy()
    exact_result["relevance_score"] = 1.0

    semantic_result = semantic_match(q, matched)

    combined = pd.concat(
        [exact_result, semantic_result]
    )

    combined = combined.sort_values(
        "relevance_score",
        ascending=False
    )

    combined = combined.drop_duplicates(
        subset=["product_id", "marketplace", "link"],
        keep="first"
    )

    if len(combined) > 0:

        combined = combined.astype(object).where(
            pd.notnull(combined),
            None
        )

        groups = group_by_product(
            combined.to_dict(orient="records")
        )

        groups.sort(
            key=lambda g: (
                -g["relevance_score"],
                g["lowest_price"] is None,
                g["lowest_price"]
            )
        )

        return jsonify(groups)

    # =========================
    # Live scraping fallback
    # =========================

    print(f"\nNo CSV result found for: {q}")
    print("Running live search...\n")

    scrape_jobs = {
        "Daraz": lambda: scrape_daraz(search_term=q, max_products=10),
        "Hukut": lambda: scrape_hukut(search_term=q, max_products=10, live_search=True),
        "Oliz": lambda: scrape_oliz(search_term=q, max_products=10),
    }

    live_results = []

    # Don't use a `with` block here: it waits for every submitted thread to
    # finish before continuing, so one scraper hanging (e.g. a slow/odd
    # page load) would block the whole request forever even though we
    # give up on that store's result after SCRAPE_TIMEOUT_SECONDS below.
    executor = ThreadPoolExecutor(max_workers=len(scrape_jobs))

    futures = {
        executor.submit(job): name
        for name, job in scrape_jobs.items()
    }

    for future in futures:
        name = futures[future]
        try:
            live_results.extend(
                future.result(timeout=SCRAPE_TIMEOUT_SECONDS)
            )
        except Exception as e:
            print(f"{name} error/timeout:", e)

    executor.shutdown(wait=False)

    live_results = filter_and_rank(live_results, q)
    live_results = assign_live_product_ids(live_results)

    if live_results:
        matched = pd.concat(
            [matched, pd.DataFrame(live_results)],
            ignore_index=True
        )

    groups = group_by_product(live_results)

    return jsonify(groups)


CATEGORY_LABELS = {
    "smartphone": "Smartphones",
    "laptop": "Laptops",
    "tablet": "Tablets",
    "smartwatch": "Smartwatches",
    "earphone": "Earphones",
}


@api.route("/categories")
def categories():

    tagged = matched[matched["search_term"].isin(CATEGORY_LABELS.keys())]
    counts = tagged["search_term"].value_counts()

    result = [
        {
            "category": key,
            "label": label,
            "count": int(counts.get(key, 0)),
        }
        for key, label in CATEGORY_LABELS.items()
    ]

    return jsonify(result)


@api.route("/category/<name>")
def category(name):

    if name not in CATEGORY_LABELS:
        return jsonify([])

    result = matched[matched["search_term"] == name].copy()
    result["relevance_score"] = 1.0

    result = result.astype(object).where(
        pd.notnull(result),
        None
    )

    groups = group_by_product(
        result.to_dict(orient="records")
    )

    groups.sort(
        key=lambda g: (
            g["lowest_price"] is None,
            g["lowest_price"]
        )
    )

    return jsonify(groups)


@api.route("/product/<product_id>")
def product(product_id):

    result = matched[
        matched["product_id"] == product_id
    ]

    result = result.sort_values(
        "price_numeric"
    )

    result = result.astype(object).where(
        pd.notnull(result),
        None
    )

    return jsonify(
        result.to_dict(
            orient="records"
        )
    )