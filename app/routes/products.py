"""Product CRUD."""
from flask import (Blueprint, render_template, redirect, url_for, request,
                   flash, current_app)
from flask_login import login_required, current_user
from sqlalchemy import or_
from app import db
from app.models import Product, CustomField, ProductCustomValue
from app.utils.forms import ProductForm
from app.utils.decorators import admin_required
from app.utils.logger import log_activity

products_bp = Blueprint("products", __name__, template_folder="../templates/products")


def _save_custom_values(product: Product, form_data) -> None:
    fields = CustomField.query.all()
    for f in fields:
        key = f"cf_{f.id}"
        val = form_data.get(key)
        if val is None: continue
        cv = ProductCustomValue.query.filter_by(product_id=product.id,
                                                field_id=f.id).first()
        if cv:
            cv.value = str(val)
        else:
            db.session.add(ProductCustomValue(product_id=product.id,
                                              field_id=f.id, value=str(val)))


@products_bp.route("/")
@login_required
def list_products():
    page = request.args.get("page", 1, type=int)
    q = request.args.get("q", "", type=str).strip()
    cat = request.args.get("category", "", type=str).strip()
    flt = request.args.get("filter", "", type=str)

    query = Product.query
    if q:
        query = query.filter(or_(Product.name.ilike(f"%{q}%"),
                                 Product.id == (int(q) if q.isdigit() else -1)))
    if cat:
        query = query.filter(Product.category.ilike(f"%{cat}%"))
    if flt == "low":
        query = query.filter(Product.quantity > 0, Product.quantity <= Product.min_stock)
    elif flt == "out":
        query = query.filter(Product.quantity <= 0)
    elif flt == "recent":
        query = query.order_by(Product.date_added.desc())
    else:
        query = query.order_by(Product.name.asc())

    pagination = query.paginate(page=page,
                                per_page=current_app.config["ITEMS_PER_PAGE"],
                                error_out=False)
    custom_fields = CustomField.query.filter_by(is_visible=True)\
                                     .order_by(CustomField.sort_order).all()
    return render_template("products/list.html", pagination=pagination,
                           q=q, cat=cat, flt=flt, custom_fields=custom_fields)


@products_bp.route("/new", methods=["GET", "POST"])
@login_required
@admin_required
def create():
    form = ProductForm()
    custom_fields = CustomField.query.order_by(CustomField.sort_order).all()
    if form.validate_on_submit():
        p = Product(name=form.name.data.strip(),
                    category=(form.category.data or "").strip() or None,
                    cost_price=form.cost_price.data,
                    selling_price=form.selling_price.data,
                    quantity=form.quantity.data,
                    min_stock=form.min_stock.data)
        db.session.add(p); db.session.flush()
        _save_custom_values(p, request.form)
        log_activity("PRODUCT_CREATE", f"Created product {p.name}",
                     product_id=p.id, new_value=p.quantity)
        db.session.commit()
        flash(f"Product '{p.name}' created.", "success")
        return redirect(url_for("products.list_products"))
    return render_template("products/form.html", form=form,
                           custom_fields=custom_fields, action="Create")


@products_bp.route("/<int:pid>/edit", methods=["GET", "POST"])
@login_required
@admin_required
def edit(pid):
    p = Product.query.get_or_404(pid)
    form = ProductForm(obj=p)
    custom_fields = CustomField.query.order_by(CustomField.sort_order).all()
    cv_map = {cv.field_id: cv.value for cv in p.custom_values}
    if form.validate_on_submit():
        prev = {"name": p.name, "qty": p.quantity, "selling_price": str(p.selling_price)}
        p.name = form.name.data.strip()
        p.category = (form.category.data or "").strip() or None
        p.cost_price = form.cost_price.data
        p.selling_price = form.selling_price.data
        p.min_stock = form.min_stock.data
        # Only update qty if admin explicitly changed it
        if int(form.quantity.data) != prev["qty"]:
            p.quantity = form.quantity.data
        _save_custom_values(p, request.form)
        log_activity("PRODUCT_UPDATE", f"Updated product {p.name}",
                     product_id=p.id, previous_value=prev, new_value=p.quantity)
        db.session.commit()
        flash("Product updated.", "success")
        return redirect(url_for("products.list_products"))
    return render_template("products/form.html", form=form, product=p,
                           custom_fields=custom_fields, cv_map=cv_map,
                           action="Edit")


@products_bp.route("/<int:pid>")
@login_required
def detail(pid):
    p = Product.query.get_or_404(pid)
    custom_fields = CustomField.query.order_by(CustomField.sort_order).all()
    cv_map = {cv.field_id: cv.value for cv in p.custom_values}
    return render_template("products/detail.html", product=p,
                           custom_fields=custom_fields, cv_map=cv_map)


@products_bp.route("/<int:pid>/delete", methods=["POST"])
@login_required
@admin_required
def delete(pid):
    p = Product.query.get_or_404(pid)
    name = p.name
    log_activity("PRODUCT_DELETE", f"Deleted product {name}",
                 product_id=p.id, previous_value=p.quantity)
    db.session.delete(p); db.session.commit()
    flash(f"Product '{name}' deleted.", "info")
    return redirect(url_for("products.list_products"))
