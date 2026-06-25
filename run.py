"""Application entry point.

Gunicorn target : gunicorn run:app
Flask dev server: python run.py  |  flask --app run.py run
"""
import os
from app import create_app, db
from app.models import (
    User, Product, Sale, Restock,
    CustomField, ProductCustomValue, ActivityLog,
)

# ── Pick config from environment ──────────────────────────────────────────────
_env = os.environ.get("FLASK_ENV", "production")

# Create app at module level so gunicorn can find `run:app`
app = create_app(_env)


@app.shell_context_processor
def make_shell_context():
    return dict(
        db=db, User=User, Product=Product, Sale=Sale,
        Restock=Restock, CustomField=CustomField,
        ProductCustomValue=ProductCustomValue, ActivityLog=ActivityLog,
    )


# ── Bootstrap DB on every cold start (idempotent) ────────────────────────────
def _bootstrap():
    """
    Create all tables if they don't exist, then ensure the default admin and
    staff accounts are present.  Safe to run on every startup — existing rows
    are never modified.
    """
    os.makedirs(app.instance_path, exist_ok=True)
    db.create_all()

    # ── Default admin ─────────────────────────────────────────────────────────
    if not User.query.filter_by(username="admin").first():
        admin = User(
            username="admin",
            email="admin@stockpilot.app",
            full_name="Administrator",
            role="admin",
            is_active=True,
        )
        admin.set_password("admin123")
        db.session.add(admin)
        app.logger.info("Created default admin account (admin / admin123)")

    # ── Default staff ─────────────────────────────────────────────────────────
    if not User.query.filter_by(username="staff").first():
        staff = User(
            username="staff",
            email="staff@stockpilot.app",
            full_name="Staff User",
            role="staff",
            is_active=True,
        )
        staff.set_password("staff123")
        db.session.add(staff)
        app.logger.info("Created default staff account (staff / staff123)")

    db.session.commit()


with app.app_context():
    _bootstrap()


if __name__ == "__main__":
    app.run(
        host="0.0.0.0",
        port=int(os.environ.get("PORT", 5000)),
        debug=(_env == "development"),
    )
