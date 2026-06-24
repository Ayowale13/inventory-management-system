"""Reports + exports."""
from flask import Blueprint, render_template, request, send_file, abort
from flask_login import login_required
import io
from app.services import report_service as rs

reports_bp = Blueprint("reports", __name__, template_folder="../templates/reports")


@reports_bp.route("/")
@login_required
def index():
    return render_template("reports/index.html",
                           daily=rs.daily_sales(),
                           weekly=rs.weekly_sales(),
                           monthly=rs.monthly_sales(),
                           low=rs.low_stock_products(),
                           out=rs.out_of_stock_products(),
                           inventory=rs.inventory_snapshot())


@reports_bp.route("/export/<period>/<fmt>")
@login_required
def export(period, fmt):
    if period == "daily": sales = rs.daily_sales()
    elif period == "weekly": sales = rs.weekly_sales()
    elif period == "monthly": sales = rs.monthly_sales()
    else: abort(404)

    if fmt == "csv":
        data = rs.sales_to_csv(sales); mime = "text/csv"; ext = "csv"
    elif fmt == "xlsx":
        data = rs.sales_to_xlsx(sales)
        mime = "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"; ext = "xlsx"
    elif fmt == "pdf":
        data = rs.sales_to_pdf(sales, f"{period.title()} Sales Report")
        mime = "application/pdf"; ext = "pdf"
    else:
        abort(404)
    return send_file(io.BytesIO(data), mimetype=mime, as_attachment=True,
                     download_name=f"{period}_sales.{ext}")
