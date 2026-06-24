"""Admin-only user management."""
from flask import Blueprint, render_template, redirect, url_for, request, flash
from flask_login import login_required, current_user
from app import db
from app.models import User
from app.utils.forms import UserForm
from app.utils.decorators import admin_required
from app.utils.logger import log_activity

users_bp = Blueprint("users", __name__, template_folder="../templates/users")


@users_bp.route("/")
@login_required
@admin_required
def list_users():
    users = User.query.order_by(User.username).all()
    return render_template("users/list.html", users=users)


@users_bp.route("/new", methods=["GET", "POST"])
@login_required
@admin_required
def create():
    form = UserForm()
    if form.validate_on_submit():
        if User.query.filter((User.username == form.username.data) |
                             (User.email == form.email.data)).first():
            flash("Username or email already exists.", "danger")
        elif not form.password.data:
            flash("Password is required for new users.", "danger")
        else:
            u = User(username=form.username.data.strip(),
                     email=form.email.data.strip(),
                     full_name=form.full_name.data, role=form.role.data,
                     is_active=form.is_active.data)
            u.set_password(form.password.data)
            db.session.add(u)
            log_activity("USER_CREATE", f"Created user {u.username}")
            db.session.commit()
            flash("User created.", "success")
            return redirect(url_for("users.list_users"))
    return render_template("users/form.html", form=form, action="Create")


@users_bp.route("/<int:uid>/edit", methods=["GET", "POST"])
@login_required
@admin_required
def edit(uid):
    u = User.query.get_or_404(uid)
    form = UserForm(obj=u)
    if form.validate_on_submit():
        u.username = form.username.data.strip()
        u.email = form.email.data.strip()
        u.full_name = form.full_name.data
        u.role = form.role.data
        u.is_active = form.is_active.data
        if form.password.data:
            u.set_password(form.password.data)
        log_activity("USER_UPDATE", f"Updated user {u.username}")
        db.session.commit()
        flash("User updated.", "success")
        return redirect(url_for("users.list_users"))
    return render_template("users/form.html", form=form, user=u, action="Edit")


@users_bp.route("/<int:uid>/delete", methods=["POST"])
@login_required
@admin_required
def delete(uid):
    if uid == current_user.id:
        flash("You cannot delete yourself.", "warning")
        return redirect(url_for("users.list_users"))
    u = User.query.get_or_404(uid)
    log_activity("USER_DELETE", f"Deleted user {u.username}")
    db.session.delete(u); db.session.commit()
    flash("User deleted.", "info")
    return redirect(url_for("users.list_users"))
