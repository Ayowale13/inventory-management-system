"""Application entry point.

Gunicorn target: gunicorn run:app
Flask dev server: python run.py  |  flask --app run.py run
"""
import os
from app import create_app, db
from app.models import (
    User, Product, Sale, Restock,
    CustomField, ProductCustomValue, ActivityLog,
)

# ── Determine config from environment ─────────────────────────────────────────
_env = os.environ.get("FLASK_ENV", "development")

# Create the app at import time so gunicorn can find `run:app`
app = create_app(_env)


@app.shell_context_processor
def make_shell_context():
    return dict(
        db=db,
        User=User,
        Product=Product,
        Sale=Sale,
        Restock=Restock,
        CustomField=CustomField,
        ProductCustomValue=ProductCustomValue,
        ActivityLog=ActivityLog,
    )


# ── Auto-initialise the database on first boot ────────────────────────────────
# On Render there are no pre-deploy hooks on the free tier, so we create
# tables on startup if they don't already exist.  This is idempotent.
with app.app_context():
    os.makedirs(app.instance_path, exist_ok=True)
    db.create_all()


if __name__ == "__main__":
    app.run(
        host="0.0.0.0",
        port=int(os.environ.get("PORT", 5000)),
        debug=(_env == "development"),
    )
