"""Lightweight JSON API."""
from flask import Blueprint, jsonify, request
from flask_login import login_required, current_user
from app.models import Product, Sale, Restock
from app.services.inventory_service import (record_sale, restock_product,
                                            InsufficientStockError)
from app import csrf

api_bp = Blueprint("api", __name__)


@api_bp.route("/products")
@login_required
def list_products():
    q = request.args.get("q", "").strip()
    query = Product.query
    if q:
        query = query.filter(Product.name.ilike(f"%{q}%"))
    items = query.order_by(Product.name).limit(50).all()
    return jsonify([{
        "id": p.id, "name": p.name, "category": p.category,
        "selling_price": float(p.selling_price), "quantity": p.quantity,
        "status": p.stock_status,
    } for p in items])


@api_bp.route("/sales", methods=["POST"])
@login_required
@csrf.exempt
def api_create_sale():
    data = request.get_json() or {}
    try:
        s = record_sale(int(data["product_id"]), int(data["quantity"]),
                        current_user.id)
        return jsonify({"ok": True, "sale_id": s.id,
                        "total": float(s.total_amount)}), 201
    except InsufficientStockError as e:
        return jsonify({"ok": False, "error": str(e)}), 409
    except (KeyError, ValueError) as e:
        return jsonify({"ok": False, "error": str(e)}), 400


@api_bp.route("/restocks", methods=["POST"])
@login_required
@csrf.exempt
def api_create_restock():
    if not current_user.is_admin:
        return jsonify({"ok": False, "error": "Forbidden"}), 403
    data = request.get_json() or {}
    try:
        r = restock_product(int(data["product_id"]), int(data["quantity_added"]),
                            current_user.id)
        return jsonify({"ok": True, "restock_id": r.id,
                        "updated_stock": r.updated_stock}), 201
    except (KeyError, ValueError) as e:
        return jsonify({"ok": False, "error": str(e)}), 400
