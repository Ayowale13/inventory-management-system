"""Application factory."""
import os
import logging
from logging.handlers import RotatingFileHandler

from flask import Flask, render_template
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_migrate import Migrate
from flask_wtf.csrf import CSRFProtect

from config import config_by_name

db = SQLAlchemy()
login_manager = LoginManager()
migrate = Migrate()
csrf = CSRFProtect()

login_manager.login_view = "auth.login"
login_manager.login_message_category = "warning"


def create_app(config_name: str | None = None) -> Flask:
    app = Flask(__name__, instance_relative_config=True)

    cfg_name = config_name or os.environ.get("FLASK_ENV", "development")
    app.config.from_object(config_by_name.get(cfg_name, config_by_name["default"]))

    # Ensure the instance folder exists (needed for SQLite)
    os.makedirs(app.instance_path, exist_ok=True)

    # ── Extensions ────────────────────────────────────────────────────────────
    db.init_app(app)
    login_manager.init_app(app)
    migrate.init_app(app, db)
    csrf.init_app(app)

    # ── User loader ───────────────────────────────────────────────────────────
    from app.models import User

    @login_manager.user_loader
    def load_user(user_id):
        # SQLAlchemy 2.x: use Session.get() instead of deprecated Query.get()
        return db.session.get(User, int(user_id))

    # ── Blueprints ────────────────────────────────────────────────────────────
    from app.routes.auth import auth_bp
    from app.routes.dashboard import dashboard_bp
    from app.routes.products import products_bp
    from app.routes.sales import sales_bp
    from app.routes.restocks import restocks_bp
    from app.routes.users import users_bp
    from app.routes.reports import reports_bp
    from app.routes.custom_fields import custom_fields_bp
    from app.routes.api import api_bp
    from app.routes.main import main_bp

    app.register_blueprint(main_bp)
    app.register_blueprint(auth_bp, url_prefix="/auth")
    app.register_blueprint(dashboard_bp, url_prefix="/dashboard")
    app.register_blueprint(products_bp, url_prefix="/products")
    app.register_blueprint(sales_bp, url_prefix="/sales")
    app.register_blueprint(restocks_bp, url_prefix="/restocks")
    app.register_blueprint(users_bp, url_prefix="/users")
    app.register_blueprint(reports_bp, url_prefix="/reports")
    app.register_blueprint(custom_fields_bp, url_prefix="/custom-fields")
    app.register_blueprint(api_bp, url_prefix="/api")

    # ── CLI commands ─────────────────────────────────────────────────────────
    from app.utils.cli import register_cli
    register_cli(app)

    # ── Error handlers ────────────────────────────────────────────────────────
    @app.errorhandler(404)
    def not_found(_):
        return render_template("errors/404.html"), 404

    @app.errorhandler(403)
    def forbidden(_):
        return render_template("errors/403.html"), 403

    @app.errorhandler(500)
    def server_error(_):
        db.session.rollback()
        return render_template("errors/500.html"), 500

    # ── Logging (stdout on Render, file in other prod environments) ───────────
    if not app.debug:
        log_handler = logging.StreamHandler()   # Render captures stdout/stderr
        log_handler.setFormatter(logging.Formatter(
            "%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]"
        ))
        log_handler.setLevel(logging.INFO)
        app.logger.addHandler(log_handler)
        app.logger.setLevel(logging.INFO)

        # Optionally also write to a rotating file (skipped on Render where
        # /logs may be read-only or ephemeral)
        if os.environ.get("LOG_TO_FILE", "false").lower() == "true":
            os.makedirs("logs", exist_ok=True)
            fh = RotatingFileHandler("logs/inventory.log",
                                     maxBytes=1_000_000, backupCount=5)
            fh.setFormatter(logging.Formatter(
                "%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]"
            ))
            fh.setLevel(logging.INFO)
            app.logger.addHandler(fh)

        app.logger.info("Inventory app started (env=%s)", cfg_name)

    return app
