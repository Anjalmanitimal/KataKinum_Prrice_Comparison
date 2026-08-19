import re
import sys
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor

ROOT_DIR = Path(__file__).resolve().parent.parent
sys.path.append(str(ROOT_DIR))
from scraper.daraz_scraper import scrape_daraz
from scraper.hukut_scraper import scrape_hukut
from scraper.oliz_scraper import scrape_oliz
from matcher.clean_products import clean_product_name, extract_price
from matcher.product_matcher import has_conflict, normalize_model
from rapidfuzz import fuzz
from price_history import record_snapshot, get_price_trend
from analytics import average_price_by_category_chart, price_trend_overview_chart, category_price_distribution_chart
from price_anomaly import compute_category_bounds, classify_anomaly
from sklearn.feature_extraction.text import TfidfVectorizer, ENGLISH_STOP_WORDS
from sklearn.metrics.pairwise import cosine_similarity
import pandas as pd
from flask import Blueprint
from flask import jsonify
from flask import request
from flask import Response

from services import matched

# Computed once from the static dataset at startup. Live-scraped rows never
# have a "category" assigned, so they can't skew this even though `matched`
# gets appended to at runtime - safe to compute once rather than per-request.
CATEGORY_PRICE_BOUNDS = compute_category_bounds(matched)

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
    "prodigee",
    "dock",
    "docking station",
    "hub",
]


def filter_and_rank(products, query):
    """Keep only live-scraped results that actually relate to the query.

    Stores don't always return an empty result set when nothing matches -
    e.g. searching "ldnio q408" (a charger not in stock) returned Hukut's
    own "trending" gaming laptops/GPUs instead, sharing zero words with the
    query. Requiring a minimum overlap discards that kind of fallback junk
    instead of just ranking it last.

    Exact-phrase matches are ranked above scattered-word matches: e.g. for
    "macbook pro", "Apple MacBook Pro M4" (the phrase appears literally)
    should outrank "MacBook Neo ... with A18 Pro chip" (both words are
    present, but only because the chip happens to be called "Pro" - it's
    a different, wrong laptop line). Word-order-independent matching still
    happens via the score, it just no longer beats a real phrase match.

    The accessory filter is skipped when the query's own words are the
    product's identity (its name/brand/model, within the same leading
    window is_accessory() checks) rather than just present anywhere -
    e.g. searching "ldnio q408" must still find "LDNIO Q408 100W GaN Fast
    Charger" (a real accessory the user explicitly asked for by name),
    while "Hagibis Docking Station ... for Macbook Pro Air Laptops" stays
    excluded from a "macbook pro" search since "macbook pro" only appears
    deep in a compatibility note, not as what this product actually is.
    """

    query_lower = query.lower().strip()
    words = [w for w in query_lower.split() if w]
    min_score = max(1, len(words) // 2)

    ranked = []
    for product in products:
        name = (product.get("product_name") or "").lower()
        lead = " ".join(name.split()[:ACCESSORY_LEAD_WORDS])

        is_the_named_item = bool(words) and all(w in lead for w in words)

        if not is_the_named_item and is_accessory(name):
            continue

        score = sum(1 for word in words if word in name)

        if score < min_score:
            continue

        exact_phrase = query_lower in name
        ranked.append((exact_phrase, score, product))

    ranked.sort(key=lambda item: (item[0], item[1]), reverse=True)

    return [product for exact_phrase, score, product in ranked]


_live_id_counter = 0
_LIVE_MATCH_THRESHOLD = 85


def assign_live_product_ids(products):
    """Groups same-batch live-scraped listings into product identities.

    Must use the same has_conflict() guard as the batch matcher
    (matcher/product_matcher.py) - without it, fuzz.token_sort_ratio alone
    scores e.g. "Apple iPhone 15 128GB Black" vs "Apple iPhone 14 128GB
    Black" at ~96% similarity, merging two different phones into one
    product_id. group_by_product() then shows whichever name was seen
    first but picks the cheapest offer across the whole merged group, so
    a search for "iphone 15" could display the iPhone 15's name with the
    iPhone 14 listing's price and store link.
    """

    global _live_id_counter

    known = []

    for product in products:

        clean_name = clean_product_name(product.get("product_name", ""))
        price_numeric = extract_price(product.get("price"))

        product["clean_name"] = clean_name
        product["price_numeric"] = price_numeric

        normalized = normalize_model(clean_name)

        matched_id = None

        for entry in known:
            similarity = fuzz.token_sort_ratio(clean_name, entry["name"])
            if similarity >= _LIVE_MATCH_THRESHOLD and not has_conflict(normalized, entry["normalized"]):
                matched_id = entry["id"]
                break

        if matched_id is None:
            _live_id_counter += 1
            matched_id = f"L{_live_id_counter:04d}"
            known.append({"id": matched_id, "name": clean_name, "normalized": normalized})

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
                "category": row.get("category"),
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
            "scraped_at": row.get("scraped_at"),
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
        group["price_anomaly"] = classify_anomaly(
            best["price_numeric"],
            group["category"],
            CATEGORY_PRICE_BOUNDS,
        )

        grouped.append(group)

    return grouped


TIER_WORDS = {
    "pro", "max", "plus", "ultra", "mini", "lite",
    "se", "fe", "air", "note", "neo", "active", "classic",
}


def find_best_deals(df, limit=12):
    """Finds the biggest real cross-store savings in the dataset.

    A naive "highest_price - lowest_price per product_id" pass would
    surface fake deals caused by product-matching mis-grouping (e.g.
    "Marshall Heston 60" and "Marshall Heston 120" - two different
    speakers - sharing a product_id, showing a fake Rs 75,000 "saving").
    To guard against that: within a group, every pair of listings must
    not have conflicting model numbers, and must not differ in a tier
    word (e.g. "Windi Mini" vs "Windi Mini Pro"), in their own product
    names (same defensive idea already used for search relevance) - if
    one listing says "60" and another says "120" with no shared number,
    or one says "Pro" and the other doesn't, the group is dropped from
    consideration rather than risk showing a wrong deal.

    This is a heuristic, not a guarantee: a shared number from a common
    product-line name (e.g. "Seiko 5 Sports SRPD85K1" and "...SRPD63"
    both contain "5" from "Seiko 5 Sports") can still let two genuinely
    different watch models through undetected, since their real model
    codes differ but the line-name number matches. Known limitation of
    the underlying product-matching pipeline, not new to this feature.
    """

    priced = df.dropna(subset=["price_numeric", "product_id"])

    deals = []

    for pid, group in priced.groupby("product_id"):

        if len(group) < 2:
            continue

        names = group["product_name"].fillna("").tolist()

        if any(is_accessory(n) for n in names):
            continue

        number_sets = [set(re.findall(r"\d+", n)) for n in names]
        tier_sets = [
            {w for w in TIER_WORDS if w in n.lower().split()}
            for n in names
        ]

        conflict = False
        for i in range(len(number_sets)):
            for j in range(i + 1, len(number_sets)):
                a, b = number_sets[i], number_sets[j]
                if a and b and not (a & b):
                    conflict = True
                    break
                if tier_sets[i] != tier_sets[j]:
                    conflict = True
                    break
            if conflict:
                break

        if conflict:
            continue

        cheapest = group.loc[group["price_numeric"].idxmin()]
        priciest = group.loc[group["price_numeric"].idxmax()]

        savings = float(priciest["price_numeric"] - cheapest["price_numeric"])

        if savings <= 0:
            continue

        deals.append({
            "product_id": pid,
            "product_name": cheapest["product_name"],
            "best_store": cheapest["marketplace"],
            "best_price": float(cheapest["price_numeric"]),
            "best_price_display": cheapest["price"],
            "highest_store": priciest["marketplace"],
            "highest_price": float(priciest["price_numeric"]),
            "highest_price_display": priciest["price"],
            "savings": savings,
            "savings_percent": round(
                savings / priciest["price_numeric"] * 100
            ),
            "store_count": len(group),
        })

    deals.sort(key=lambda d: d["savings"], reverse=True)

    return deals[:limit]


SEMANTIC_MIN_SCORE = 0.4


ACCESSORY_LEAD_WORDS = 10


def is_accessory(name):
    """Checks only the first few words of the name, not the whole string.

    A real product occasionally bundles or mentions an accessory deep in
    its spec list (e.g. "Samsung Galaxy A17 5G ... With 25W Power
    Adapter") - that shouldn't disqualify it. Genuine accessory listings
    almost always name the accessory itself up front (e.g. "PITAKA
    Monogram Edge Case for iPhone...", "Samsung 60W Power Adapter").
    """

    name = (name or "").lower()
    lead = " ".join(name.split()[:ACCESSORY_LEAD_WORDS])
    return any(word in lead for word in ACCESSORY_WORDS)


def semantic_match(query, df, text_column="clean_name", top_k=40):
    """TF-IDF + cosine similarity search, layered on top of exact matching.

    Finds products related to the query in meaning/wording even when the
    query isn't a literal substring of the product name (e.g. word order
    differs, or the query only shares some words with the name).

    SEMANTIC_MIN_SCORE is deliberately strict (0.4): short e-commerce
    titles easily score 0.2-0.35 on shared generic words alone. A high bar
    means precise queries only return close variants, and looser
    natural-language queries that don't score highly against anything
    correctly fall through to live scraping instead of returning wrong
    results.

    The score threshold alone isn't enough, though: a single shared word
    can still score above 0.4 if that word is rare across the catalog
    (high IDF weight) - e.g. "macbook pro" scored 0.44 against "Apple
    MacBook Neo 2026" purely because both contain "macbook"; "pro" wasn't
    in that product's name at all. So every meaningful word in the query
    (i.e. excluding English stop words, same as the vectorizer ignores)
    must literally appear in the candidate - word order can differ, but no
    word can be missing. This makes semantic search strictly a "same words,
    possibly reordered" matcher rather than a "textually similar, close
    enough" matcher, so it never substitutes a different product/model.
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

    query_words = [
        w for w in query.lower().split()
        if w and w not in ENGLISH_STOP_WORDS
    ]

    if query_words:
        def has_all_query_words(name):
            name_words = set(str(name).lower().split())
            return all(w in name_words for w in query_words)

        scored = scored[
            scored[text_column].fillna("").apply(has_all_query_words)
        ]

    scored = scored[scored["relevance_score"] >= SEMANTIC_MIN_SCORE]
    scored = scored.sort_values("relevance_score", ascending=False)

    return scored.head(top_k)


@api.route("/")
def home():

    return jsonify({
        "message": "Kata Kinum API Running"
    })


@api.route("/deals")
def deals():

    result = find_best_deals(matched)

    for deal in result:
        trend = get_price_trend(deal["product_id"])

        if trend["status"] == "ok":
            deal["price_trend"] = trend["trend"]
        else:
            deal["price_trend"] = None

    # Deals with a confirmed falling price are the most actionable - a
    # real gap the tracker has also watched get cheaper over time, not
    # just a snapshot difference - so they're worth surfacing first,
    # ahead of deals ranked purely by raw savings amount.
    result.sort(key=lambda d: d["price_trend"] == "falling", reverse=True)

    return jsonify(result)


@api.route("/analytics/average-price-by-category.png")
def analytics_average_price_by_category():

    png_bytes = average_price_by_category_chart(matched)

    return Response(png_bytes, mimetype="image/png")


@api.route("/analytics/category-price-distribution.png")
def analytics_category_price_distribution():

    png_bytes = category_price_distribution_chart(matched)

    return Response(png_bytes, mimetype="image/png")


@api.route("/analytics/price-trend-overview.png")
def analytics_price_trend_overview():
    # Reads the clearly-labeled SIMULATED demo history CSV, never the
    # real price_history table in the database - see
    # matcher/generate_demo_price_history.py for why. If that file
    # doesn't exist yet, this returns a 404 rather than silently falling
    # back to (insufficient) real data.

    try:
        demo_history = pd.read_csv("data/processed/price_history_demo.csv")
    except FileNotFoundError:
        return jsonify({
            "error": "Demo price history not generated yet. Run "
                     "matcher/generate_demo_price_history.py first."
        }), 404

    png_bytes = price_trend_overview_chart(demo_history)

    return Response(png_bytes, mimetype="image/png")


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

    combined = combined[
        ~combined["product_name"].fillna("").apply(is_accessory)
    ]

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

        record_snapshot(groups)

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

    # Drop listings with no parseable price (e.g. a scraped UI element like
    # "VIEW VARIANTS" rather than an actual product) - useless on a price
    # comparison site regardless of what it is.
    live_results = [
        p for p in live_results if p.get("price_numeric") is not None
    ]

    if live_results:
        matched = pd.concat(
            [matched, pd.DataFrame(live_results)],
            ignore_index=True
        )

    groups = group_by_product(live_results)

    record_snapshot(groups)

    return jsonify(groups)


CATEGORY_LABELS = {
    "smartphone": "Smartphones",
    "laptop": "Laptops",
    "tablet": "Tablets",
    "smartwatch": "Smartwatches",
    "earphone": "Earphones",
    "bag": "Bags & Backpacks",
    "watch": "Watches",
    "camera_gear": "Drones & Camera Gear",
    "powerbank": "Power Banks & Chargers",
    "audio": "Speakers & Audio",
    "appliance": "Home Appliances",
}


@api.route("/categories")
def categories():

    tagged = matched[matched["category"].isin(CATEGORY_LABELS.keys())]
    counts = tagged["category"].value_counts()

    result = [
        {
            "category": key,
            "label": label,
            "count": int(counts.get(key, 0)),
        }
        for key, label in CATEGORY_LABELS.items()
        if counts.get(key, 0) > 0
    ]

    return jsonify(result)


@api.route("/category/<name>")
def category(name):

    if name not in CATEGORY_LABELS:
        return jsonify([])

    result = matched[matched["category"] == name].copy()
    result["relevance_score"] = 1.0

    result = result[
        ~result["product_name"].fillna("").apply(is_accessory)
    ]

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

    record_snapshot(groups)

    return jsonify(groups)


@api.route("/product/<product_id>/trend")
def product_trend(product_id):

    return jsonify(get_price_trend(product_id))


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