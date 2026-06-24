"""Sales recording."""
from flask import Blueprint, render_template, redirect, url_for, request, flash, current_app
from flask_login import login_required, current_user
from app.models import Product, Sale
from app.utils.forms import SaleForm
from app.services.inventory_service import record_sale, InsufficientStockError

sales_bp = Blueprint("sales", __name__, template_folder="../templates/sales")


@sales_bp.route("/", methods=["GET", "POST"])
@login_required
def new_sale():
    form = SaleForm()
    q = request.args.get("q", "").strip()
    products = []
    if q:
        products = Product.query.filter(Product.name.ilike(f"%{q}%")).limit(20).all()

    if form.validate_on_submit():
        try:
            sale = record_sale(int(form.product_id.data), form.quantity.data,
                               current_user.id)
            flash(f"Sale recorded. Total: {sale.total_amount}", "success")
            return redirect(url_for("sales.history"))
        except InsufficientStockError as e:
            flash(str(e), "danger")
        except ValueError as e:
            flash(str(e), "danger")
    return render_template("sales/new.html", form=form, products=products, q=q)


@sales_bp.route("/history")
@login_required
def history():
    page = request.args.get("page", 1, type=int)
    pagination = Sale.query.order_by(Sale.created_at.desc())\
        .paginate(page=page, per_page=current_app.config["ITEMS_PER_PAGE"],
                  error_out=False)
    return render_template("sales/history.html", pagination=pagination)
