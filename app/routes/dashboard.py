"""Dashboard with KPIs."""
from datetime import datetime, timedelta
from decimal import Decimal
from flask import Blueprint, render_template
from flask_login import login_required
from sqlalchemy import func
from app import db
from app.models import Product, Sale, Restock

dashboard_bp = Blueprint("dashboard", __name__, template_folder="../templates")


@dashboard_bp.route("/")
@login_required
def index():
    today_start = datetime.combine(datetime.utcnow().date(), datetime.min.time())

    total_products = Product.query.count()
    total_quantity = db.session.query(func.coalesce(func.sum(Product.quantity), 0)).scalar()

    today_sales = Sale.query.filter(Sale.created_at >= today_start).all()
    total_sales_today = len(today_sales)
    total_revenue_today = sum((Decimal(str(s.total_amount)) for s in today_sales),
                              Decimal("0"))

    low_stock = Product.query.filter(Product.quantity > 0,
                                     Product.quantity <= Product.min_stock).all()
    out_of_stock = Product.query.filter(Product.quantity <= 0).all()

    recent_sales = Sale.query.order_by(Sale.created_at.desc()).limit(10).all()
    recent_restocks = Restock.query.order_by(Restock.created_at.desc()).limit(10).all()

    # chart: last 7 days revenue
    days, revenues = [], []
    for i in range(6, -1, -1):
        d = datetime.utcnow().date() - timedelta(days=i)
        start = datetime.combine(d, datetime.min.time())
        end = start + timedelta(days=1)
        rev = db.session.query(func.coalesce(func.sum(Sale.total_amount), 0))\
                        .filter(Sale.created_at >= start, Sale.created_at < end).scalar()
        days.append(d.strftime("%a"))
        revenues.append(float(rev or 0))

    return render_template("dashboard.html",
        total_products=total_products,
        total_quantity=total_quantity,
        total_sales_today=total_sales_today,
        total_revenue_today=total_revenue_today,
        low_stock=low_stock, out_of_stock=out_of_stock,
        recent_sales=recent_sales, recent_restocks=recent_restocks,
        chart_days=days, chart_revenues=revenues,
    )
