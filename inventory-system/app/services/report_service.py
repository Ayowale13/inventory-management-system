"""Report generation: PDF, Excel, CSV."""
import csv, io
from datetime import datetime, timedelta
from sqlalchemy import func
from app import db
from app.models import Sale, Product, Restock


def sales_between(start, end):
    return Sale.query.filter(Sale.created_at >= start, Sale.created_at < end)\
                     .order_by(Sale.created_at.desc()).all()


def daily_sales(date=None):
    date = date or datetime.utcnow().date()
    start = datetime.combine(date, datetime.min.time())
    return sales_between(start, start + timedelta(days=1))


def weekly_sales():
    end = datetime.utcnow()
    return sales_between(end - timedelta(days=7), end + timedelta(seconds=1))


def monthly_sales():
    end = datetime.utcnow()
    return sales_between(end - timedelta(days=30), end + timedelta(seconds=1))


def sales_to_csv(sales) -> bytes:
    buf = io.StringIO()
    w = csv.writer(buf)
    w.writerow(["ID", "Date", "Product", "Quantity", "Unit Price",
                "Total", "Cashier"])
    for s in sales:
        w.writerow([s.id, s.created_at.strftime("%Y-%m-%d %H:%M"),
                    s.product.name, s.quantity, s.unit_price,
                    s.total_amount, s.cashier.username])
    return buf.getvalue().encode("utf-8")


def sales_to_xlsx(sales) -> bytes:
    from openpyxl import Workbook
    wb = Workbook(); ws = wb.active; ws.title = "Sales"
    ws.append(["ID", "Date", "Product", "Quantity", "Unit Price",
               "Total", "Cashier"])
    for s in sales:
        ws.append([s.id, s.created_at.strftime("%Y-%m-%d %H:%M"),
                   s.product.name, s.quantity, float(s.unit_price),
                   float(s.total_amount), s.cashier.username])
    buf = io.BytesIO(); wb.save(buf); return buf.getvalue()


def sales_to_pdf(sales, title="Sales Report") -> bytes:
    from reportlab.lib.pagesizes import A4
    from reportlab.lib import colors
    from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
    from reportlab.lib.styles import getSampleStyleSheet
    buf = io.BytesIO()
    doc = SimpleDocTemplate(buf, pagesize=A4)
    styles = getSampleStyleSheet()
    data = [["ID", "Date", "Product", "Qty", "Unit Price", "Total", "Cashier"]]
    total = 0
    for s in sales:
        data.append([s.id, s.created_at.strftime("%Y-%m-%d %H:%M"),
                     s.product.name, s.quantity, f"{s.unit_price:.2f}",
                     f"{s.total_amount:.2f}", s.cashier.username])
        total += float(s.total_amount)
    table = Table(data, repeatRows=1)
    table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#0d6efd")),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
        ("GRID", (0, 0), (-1, -1), 0.25, colors.grey),
        ("FONTSIZE", (0, 0), (-1, -1), 9),
    ]))
    doc.build([Paragraph(title, styles["Title"]), Spacer(1, 12), table,
               Spacer(1, 12), Paragraph(f"<b>Grand Total: {total:,.2f}</b>",
                                        styles["Normal"])])
    return buf.getvalue()


def inventory_snapshot():
    return Product.query.order_by(Product.name).all()


def low_stock_products():
    return Product.query.filter(Product.quantity > 0,
                                Product.quantity <= Product.min_stock).all()


def out_of_stock_products():
    return Product.query.filter(Product.quantity <= 0).all()
