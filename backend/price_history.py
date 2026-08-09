from datetime import datetime, timezone

import numpy as np
import pandas as pd
from sklearn.linear_model import LinearRegression

from db import load_price_history, save_price_history

MIN_HISTORY_POINTS = 3
TREND_THRESHOLD = 0.01


def record_snapshot(groups):
    """Log one price observation per product for today's date.

    Called every time a product's lowest price is shown to a user (via
    search or category browsing). Real history builds up over real usage
    over multiple days/sessions - it is deliberately not backfilled with
    fabricated historical points. Re-observing the same product on the
    same day updates that day's row rather than duplicating it, so
    repeated searches don't bloat the log.
    """

    today = datetime.now(timezone.utc).date().isoformat()

    new_rows = [
        {
            "product_id": g["product_id"],
            "price_numeric": g["lowest_price"],
            "recorded_at": today,
        }
        for g in groups
        if g.get("lowest_price") is not None
    ]

    if not new_rows:
        return

    existing = load_price_history()
    combined = pd.concat([existing, pd.DataFrame(new_rows)], ignore_index=True)

    combined.drop_duplicates(
        subset=["product_id", "recorded_at"],
        keep="last",
        inplace=True
    )

    save_price_history(combined)


def get_price_trend(product_id):
    """Fit a linear trend over a product's recorded price history.

    Honest by design: with fewer than MIN_HISTORY_POINTS observations,
    there isn't enough data for a trend to mean anything, so this reports
    that plainly instead of guessing.
    """

    df = load_price_history()
    history = df[df["product_id"] == product_id].sort_values("recorded_at")

    points = [
        {"date": row["recorded_at"], "price": row["price_numeric"]}
        for _, row in history.iterrows()
    ]

    if len(points) < MIN_HISTORY_POINTS:
        points_needed = MIN_HISTORY_POINTS - len(points)

        return {
            "status": "insufficient_data",
            "points": points,
            "current": points[-1]["price"] if points else None,
            "first_tracked": points[0]["date"] if points else None,
            "points_needed": points_needed,
            "message": (
                f"Tracking started - {len(points)} price point"
                f"{'s' if len(points) != 1 else ''} recorded so far. "
                f"{points_needed} more visit{'s' if points_needed != 1 else ''} "
                "needed before a trend can be shown."
            ),
        }

    x = np.arange(len(points)).reshape(-1, 1)
    y = np.array([p["price"] for p in points], dtype=float)

    model = LinearRegression()
    model.fit(x, y)
    slope = model.coef_[0]

    relative_slope = slope / y.mean() if y.mean() else 0

    if relative_slope < -TREND_THRESHOLD:
        trend = "falling"
        recommendation = "Price has been trending down recently - might be worth waiting."
    elif relative_slope > TREND_THRESHOLD:
        trend = "rising"
        recommendation = "Price has been trending up recently - buying now may beat a further rise."
    else:
        trend = "stable"
        recommendation = "Price has been stable recently."

    return {
        "status": "ok",
        "points": points,
        "trend": trend,
        "recommendation": recommendation,
        "lowest_recorded": float(y.min()),
        "highest_recorded": float(y.max()),
        "current": float(y[-1]),
    }
