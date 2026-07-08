import pandas as pd
from flask import Blueprint
from flask import jsonify
from flask import request

from services import recommendations
from services import matched

api = Blueprint("api", __name__)


@api.route("/")
def home():

    return jsonify({
        "message": "Kata Kinum API Running"
    })


@api.route("/search")
def search():

    q = request.args.get("q", "").lower()

    if q == "":
        return jsonify([])

    result = matched[
        matched["product_name"]
        .str.lower()
        .str.contains(q, na=False)
    ]

    grouped = (
        result
        .sort_values("price_numeric")
        .groupby("product_id")
        .first()
        .reset_index()
    )

    # Replace NaN with None
    grouped = grouped.astype(object).where(pd.notnull(grouped), None)

    return jsonify(grouped.to_dict(orient="records"))


@api.route("/product/<product_id>")
def product(product_id):

    result = matched[
        matched["product_id"] == product_id
    ]

    result = result.sort_values(
        "price_numeric"
    )

    return jsonify(
        result.to_dict(
            orient="records"
        )
    )