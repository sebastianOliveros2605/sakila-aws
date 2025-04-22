# routes/staff.py
from flask import Blueprint, jsonify, request
from .models import Staff

staff_bp = Blueprint("staff", __name__)

@staff_bp.route("/staff", methods=["GET"])
def get_staff():
    store_id = request.args.get("store_id", type=int)

    if store_id is None:
        return jsonify({"error": "Debe proporcionar el store_id como query param"}), 400

    staff = Staff.query.filter_by(store_id=store_id).all()
    
    staff_list = [
        {
            "staff_id": s.staff_id,
            "first_name": s.first_name,
            "last_name": s.last_name,
            "store_id": s.store_id
        } for s in staff
    ]
    
    return jsonify(staff_list)

