# routes/store.py
from flask import Blueprint, jsonify
from .models import Store

store_bp = Blueprint("store", __name__)

@store_bp.route("/stores", methods=["GET"])
def get_stores():
    stores = Store.query.all()
    store_list = [{"store_id": s.store_id} for s in stores]
    return jsonify(store_list)
