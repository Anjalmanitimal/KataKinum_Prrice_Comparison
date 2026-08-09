import io

import numpy as np
import matplotlib
matplotlib.use("Agg")  # non-interactive backend - safe to render inside Flask
import matplotlib.pyplot as plt
from sklearn.linear_model import LinearRegression

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

BRAND_COLOR = "#6366f1"
INK_COLOR = "#0b1220"


def _fig_to_png_bytes(fig):
    buffer = io.BytesIO()
    fig.savefig(buffer, format="png", dpi=150, bbox_inches="tight")
    plt.close(fig)
    buffer.seek(0)
    return buffer.getvalue()


def average_price_by_category_chart(df):
    """Bar chart of mean price per category, cheapest to most expensive.

    Only categories with a priced product are shown - a category with no
    valid price_numeric values would otherwise plot as an empty/zero bar,
    which would misrepresent it as "free" rather than "no data".
    """

    priced = df.dropna(subset=["price_numeric", "category"])

    averages = (
        priced.groupby("category")["price_numeric"]
        .mean()
        .sort_values()
    )

    labels = [CATEGORY_LABELS.get(cat, cat) for cat in averages.index]
    values = averages.values

    fig, ax = plt.subplots(figsize=(9, 5.5))

    bars = ax.barh(labels, values, color=BRAND_COLOR)

    ax.set_xlabel("Average price (Rs)")
    ax.set_title("Average Price by Category", fontsize=14, fontweight="bold", color=INK_COLOR)
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    ax.xaxis.set_major_formatter(lambda x, _: f"{x:,.0f}")

    for bar, value in zip(bars, values):
        ax.text(
            bar.get_width() + (values.max() * 0.01),
            bar.get_y() + bar.get_height() / 2,
            f"Rs {value:,.0f}",
            va="center",
            fontsize=9,
            color=INK_COLOR,
        )

    fig.tight_layout()

    return _fig_to_png_bytes(fig)


TREND_MIN_POINTS = 3
TREND_THRESHOLD = 0.01  # matches backend/price_history.py's real trend classifier


def _classify_trend(prices):
    if len(prices) < TREND_MIN_POINTS:
        return None

    x = np.arange(len(prices)).reshape(-1, 1)
    y = np.array(prices, dtype=float)

    model = LinearRegression()
    model.fit(x, y)
    slope = model.coef_[0]

    relative_slope = slope / y.mean() if y.mean() else 0

    if relative_slope < -TREND_THRESHOLD:
        return "falling"
    if relative_slope > TREND_THRESHOLD:
        return "rising"
    return "stable"


def price_trend_overview_chart(history_df):
    """Bar chart of how many tracked products are trending up/down/stable.

    IMPORTANT: intended for demo/simulated history only (see
    matcher/generate_demo_price_history.py) - never call this with real
    price_history.csv data and present it as a real trend summary while
    there isn't enough real history to back it. The "(simulated demo
    data)" label is baked into the chart image itself, not just shown
    around it in the UI, so the disclosure survives even if the image is
    saved or shared on its own.
    """

    counts = {"falling": 0, "stable": 0, "rising": 0}

    for _, group in history_df.groupby("product_id"):
        prices = group.sort_values("recorded_at")["price_numeric"].tolist()
        trend = _classify_trend(prices)
        if trend in counts:
            counts[trend] += 1

    labels = ["Falling", "Stable", "Rising"]
    values = [counts["falling"], counts["stable"], counts["rising"]]
    colors = ["#059669", "#64748b", "#dc2626"]

    fig, ax = plt.subplots(figsize=(7, 5.5))

    bars = ax.bar(labels, values, color=colors, width=0.55)

    ax.set_ylabel("Number of products")
    ax.set_title(
        "Price Trend Overview\n(simulated demo data)",
        fontsize=14,
        fontweight="bold",
        color=INK_COLOR,
    )
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)

    for bar, value in zip(bars, values):
        ax.text(
            bar.get_x() + bar.get_width() / 2,
            bar.get_height() + (max(values, default=1) * 0.02),
            str(value),
            ha="center",
            fontsize=12,
            fontweight="bold",
            color=INK_COLOR,
        )

    fig.tight_layout()

    return _fig_to_png_bytes(fig)
