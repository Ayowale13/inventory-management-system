"""Custom Flask CLI commands."""
import click
from flask.cli import with_appcontext
from app import db


def register_cli(app):
    @app.cli.command("init-db")
    @with_appcontext
    def init_db():
        """Create all tables."""
        db.create_all()
        click.echo("Database initialized.")

    @app.cli.command("create-admin")
    @click.option("--username", prompt=True)
    @click.option("--email", prompt=True)
    @click.option("--password", prompt=True, hide_input=True, confirmation_prompt=True)
    @with_appcontext
    def create_admin(username, email, password):
        """Create an admin user."""
        from app.models import User
        if User.query.filter((User.username == username) | (User.email == email)).first():
            click.echo("User already exists."); return
        u = User(username=username, email=email, full_name=username, role="admin")
        u.set_password(password)
        db.session.add(u); db.session.commit()
        click.echo(f"Admin '{username}' created.")

    @app.cli.command("seed")
    @with_appcontext
    def seed():
        """Seed demo data."""
        from app.models import User, Product
        if not User.query.filter_by(username="admin").first():
            admin = User(username="admin", email="admin@example.com",
                         full_name="Administrator", role="admin")
            admin.set_password("admin123")
            db.session.add(admin)
        if not User.query.filter_by(username="staff").first():
            staff = User(username="staff", email="staff@example.com",
                         full_name="Staff User", role="staff")
            staff.set_password("staff123")
            db.session.add(staff)
        samples = [
            ("Rice (50kg)", "Grains", 35000, 42000, 50, 10),
            ("Cooking Oil 5L", "Groceries", 7000, 9500, 30, 5),
            ("Sugar 1kg", "Groceries", 800, 1200, 100, 20),
            ("Indomie Carton", "Noodles", 6000, 7500, 25, 5),
            ("Milk Powder 500g", "Dairy", 2500, 3500, 40, 8),
        ]
        for n, c, cp, sp, q, m in samples:
            if not Product.query.filter_by(name=n).first():
                db.session.add(Product(name=n, category=c, cost_price=cp,
                                       selling_price=sp, quantity=q, min_stock=m))
        db.session.commit()
        click.echo("Seed complete. Login admin/admin123 or staff/staff123.")
