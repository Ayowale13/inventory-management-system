"""Authentication routes."""
from datetime import datetime
from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_user, logout_user, login_required, current_user
from app import db
from app.models import User
from app.utils.forms import LoginForm
from app.utils.logger import log_activity

auth_bp = Blueprint("auth", __name__, template_folder="../templates/auth")


@auth_bp.route("/login", methods=["GET", "POST"])
def login():
    if current_user.is_authenticated:
        return redirect(url_for("dashboard.index"))
    form = LoginForm()
    if form.validate_on_submit():
        u = User.query.filter_by(username=form.username.data.strip()).first()
        if u and u.is_active and u.check_password(form.password.data):
            login_user(u)
            u.last_login = datetime.utcnow()
            log_activity("LOGIN", f"{u.username} logged in")
            db.session.commit()
            flash(f"Welcome back, {u.full_name or u.username}!", "success")
            return redirect(request.args.get("next") or url_for("dashboard.index"))
        flash("Invalid credentials or account disabled.", "danger")
    return render_template("auth/login.html", form=form)


@auth_bp.route("/logout")
@login_required
def logout():
    log_activity("LOGOUT", f"{current_user.username} logged out")
    db.session.commit()
    logout_user()
    flash("You have been logged out.", "info")
    return redirect(url_for("auth.login"))
