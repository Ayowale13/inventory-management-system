"""Authentication routes."""
from datetime import datetime, timezone
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
        username = form.username.data.strip()
        password = form.password.data

        # Look up by username (case-sensitive, matches how we store it)
        u = User.query.filter_by(username=username).first()

        if u is None:
            app_logger_warn(f"Login attempt for unknown username: {username!r}")
            flash("Invalid credentials or account disabled.", "danger")
            return render_template("auth/login.html", form=form)

        if not u.is_active:
            flash("Invalid credentials or account disabled.", "danger")
            return render_template("auth/login.html", form=form)

        if not u.check_password(password):
            app_logger_warn(f"Bad password for user {username!r}")
            flash("Invalid credentials or account disabled.", "danger")
            return render_template("auth/login.html", form=form)

        # ── Successful login ──────────────────────────────────────────────────
        login_user(u, remember=False)
        u.last_login = datetime.now(timezone.utc).replace(tzinfo=None)
        log_activity("LOGIN", f"{u.username} logged in")
        db.session.commit()

        flash(f"Welcome back, {u.full_name or u.username}!", "success")
        next_page = request.args.get("next")
        # Guard against open-redirect
        if next_page and next_page.startswith("/"):
            return redirect(next_page)
        return redirect(url_for("dashboard.index"))

    return render_template("auth/login.html", form=form)


def app_logger_warn(msg: str) -> None:
    """Log a warning safely (no-op if no app context logger is available)."""
    try:
        from flask import current_app
        current_app.logger.warning(msg)
    except RuntimeError:
        pass


@auth_bp.route("/logout")
@login_required
def logout():
    log_activity("LOGOUT", f"{current_user.username} logged out")
    db.session.commit()
    logout_user()
    flash("You have been logged out.", "info")
    return redirect(url_for("auth.login"))
