"""Restock operations."""
from flask import Blueprint, render_template, redirect, url_for, request, flash, current_app
from flask_login import login_required, current_user
from app.models import Product, Restock
from app.utils.forms import RestockForm
from app.utils.decorators import admin_required
from app.services.inventory_service import restock_product

restocks_bp = Blueprint("restocks", __name__, template_folder="../templates/restocks")


@restocks_bp.route("/", methods=["GET", "POST"])
@login_required
@admin_required
def new_restock():
    form = RestockForm()
    q = request.args.get("q", "").strip()
    products = []
    if q:
        products = Product.query.filter(Product.name.ilike(f"%{q}%")).limit(20).all()

    if form.validate_on_submit():
        try:
            r = restock_product(int(form.product_id.data),
                                form.quantity_added.data, current_user.id)
            flash(f"Restocked. New stock: {r.updated_stock}", "success")
            return redirect(url_for("restocks.history"))
        except ValueError as e:
            flash(str(e), "danger")
    return render_template("restocks/new.html", form=form, products=products, q=q)


@restocks_bp.route("/history")
@login_required
def history():
    page = request.args.get("page", 1, type=int)
    pagination = Restock.query.order_by(Restock.created_at.desc())\
        .paginate(page=page, per_page=current_app.config["ITEMS_PER_PAGE"],
                  error_out=False)
    return render_template("restocks/history.html", pagination=pagination)
