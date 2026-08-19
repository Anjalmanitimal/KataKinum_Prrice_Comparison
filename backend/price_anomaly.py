"""
Flags products priced unusually high or low for their category, using the
IQR (interquartile range) method - a standard, well-established statistical
outlier detection technique, not a trained model.

This is genuine "price intelligence" beyond cross-store comparison: instead
of only asking "which store is cheapest for this exact product," it asks
"is this price actually unusual compared to the rest of the market for
this kind of product." It also doubles as a data-quality safety net - a
scraper bug that captures a wildly wrong price would show up as an extreme
outlier here too.

Bounds are computed once per category across the whole dataset, then any
product's lowest price is checked against its own category's bounds.
Categories with very few products (e.g. "appliance" with 7) give a less
statistically reliable bound than a category with 30+ - a known limitation
of applying IQR to small samples, worth noting rather than hiding.
"""

IQR_MULTIPLIER = 1.5


def compute_category_bounds(df):
    """Returns {category: (lower_bound, upper_bound)} from real price data."""

    bounds = {}

    priced = df.dropna(subset=["price_numeric", "category"])

    for category, group in priced.groupby("category"):
        prices = group["price_numeric"]

        q1 = prices.quantile(0.25)
        q3 = prices.quantile(0.75)
        iqr = q3 - q1

        lower = max(q1 - IQR_MULTIPLIER * iqr, 0)
        upper = q3 + IQR_MULTIPLIER * iqr

        bounds[category] = (lower, upper)

    return bounds


def classify_anomaly(price, category, bounds):
    """Returns "cheap", "expensive", or None."""

    if price is None or category not in bounds:
        return None

    lower, upper = bounds[category]

    if price < lower:
        return "cheap"
    if price > upper:
        return "expensive"

    return None
