"""Dynamic custom field management."""
from flask import Blueprint, render_template, redirect, url_for, request, flash
from flask_login import login_required
from app import db
from app.models import CustomField
from app.utils.forms import CustomFieldForm
from app.utils.decorators import admin_required

custom_fields_bp = Blueprint("custom_fields", __name__,
                             template_folder="../templates/custom_fields")


@custom_fields_bp.route("/")
@login_required
@admin_required
def list_fields():
    fields = CustomField.query.order_by(CustomField.sort_order).all()
    return render_template("custom_fields/list.html", fields=fields)


@custom_fields_bp.route("/new", methods=["GET", "POST"])
@login_required
@admin_required
def create():
    form = CustomFieldForm()
    if form.validate_on_submit():
        if CustomField.query.filter_by(name=form.name.data).first():
            flash("Internal name already exists.", "danger")
        else:
            f = CustomField(name=form.name.data.strip().replace(" ", "_"),
                            label=form.label.data, field_type=form.field_type.data,
                            is_visible=form.is_visible.data,
                            sort_order=form.sort_order.data)
            db.session.add(f); db.session.commit()
            flash("Field created.", "success")
            return redirect(url_for("custom_fields.list_fields"))
    return render_template("custom_fields/form.html", form=form, action="Create")


@custom_fields_bp.route("/<int:fid>/edit", methods=["GET", "POST"])
@login_required
@admin_required
def edit(fid):
    f = CustomField.query.get_or_404(fid)
    form = CustomFieldForm(obj=f)
    if form.validate_on_submit():
        f.label = form.label.data
        f.field_type = form.field_type.data
        f.is_visible = form.is_visible.data
        f.sort_order = form.sort_order.data
        db.session.commit()
        flash("Field updated.", "success")
        return redirect(url_for("custom_fields.list_fields"))
    return render_template("custom_fields/form.html", form=form, action="Edit")


@custom_fields_bp.route("/<int:fid>/delete", methods=["POST"])
@login_required
@admin_required
def delete(fid):
    f = CustomField.query.get_or_404(fid)
    db.session.delete(f); db.session.commit()
    flash("Field deleted.", "info")
    return redirect(url_for("custom_fields.list_fields"))


@custom_fields_bp.route("/<int:fid>/toggle", methods=["POST"])
@login_required
@admin_required
def toggle(fid):
    f = CustomField.query.get_or_404(fid)
    f.is_visible = not f.is_visible
    db.session.commit()
    return redirect(url_for("custom_fields.list_fields"))
