"""Core business logic for stock movements with transactional safety."""
from decimal import Decimal
from app import db
from app.models import Product, Sale, Restock
from app.utils.logger import log_activity


class InsufficientStockError(Exception):
    pass


def record_sale(product_id: int, quantity: int, user_id: int) -> Sale:
    """
    Record a sale and deduct stock atomically.
    Remaining Stock = Current Stock - Quantity Purchased
    Stock can never go negative.
    """
    if quantity <= 0:
        raise ValueError("Quantity must be greater than zero.")

    try:
        product = db.session.query(Product).with_for_update(of=Product, nowait=False)\
                                           .filter_by(id=product_id).first()
        if not product:
            raise ValueError("Product not found.")
        if product.quantity < quantity:
            raise InsufficientStockError(
                f"Insufficient stock available. Only {product.quantity} left."
            )

        unit_price = Decimal(str(product.selling_price))
        total = unit_price * Decimal(quantity)

        sale = Sale(product_id=product.id, user_id=user_id, quantity=quantity,
                    unit_price=unit_price, total_amount=total)

        previous_qty = product.quantity
        product.quantity = previous_qty - quantity
        db.session.add(sale)

        log_activity("SALE", f"Sold {quantity} x {product.name} = {total}",
                     product_id=product.id,
                     previous_value=previous_qty, new_value=product.quantity)
        db.session.commit()
        return sale
    except Exception:
        db.session.rollback()
        raise


def restock_product(product_id: int, quantity_added: int, user_id: int) -> Restock:
    """
    Add quantity to a product.
    Updated Stock = Current Stock + Quantity Added
    """
    if quantity_added <= 0:
        raise ValueError("Quantity added must be greater than zero.")

    try:
        product = db.session.query(Product).with_for_update(of=Product, nowait=False)\
                                           .filter_by(id=product_id).first()
        if not product:
            raise ValueError("Product not found.")

        prev = product.quantity
        product.quantity = prev + quantity_added

        rec = Restock(product_id=product.id, user_id=user_id,
                      previous_stock=prev, quantity_added=quantity_added,
                      updated_stock=product.quantity)
        db.session.add(rec)
        log_activity("RESTOCK", f"Restocked {quantity_added} x {product.name}",
                     product_id=product.id, previous_value=prev,
                     new_value=product.quantity)
        db.session.commit()
        return rec
    except Exception:
        db.session.rollback()
        raise
