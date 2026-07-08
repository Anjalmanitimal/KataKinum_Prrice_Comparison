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

    q = request.args.get(
        "q",
        ""
    ).lower()

    if q == "":
        return jsonify([])

    result = recommendations[
        recommendations["product_name"]
        .str.lower()
        .str.contains(
            q,
            na=False
        )
    ]

    return jsonify(
        result.to_dict(
            orient="records"
        )
    )


@api.route("/product/<product_id>")
def product(product_id):

    result = matched[
        matched["product_id"] == product_id
    ]

    return jsonify(
        result.to_dict(
            orient="records"
        )
    )