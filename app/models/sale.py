"""Sale (sales record) model."""
from datetime import datetime, timezone
from app import db


def _utcnow():
    return datetime.now(timezone.utc).replace(tzinfo=None)


class Sale(db.Model):
    __tablename__ = "sales"

    id = db.Column(db.Integer, primary_key=True)
    product_id = db.Column(db.Integer, db.ForeignKey("products.id"), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    quantity = db.Column(db.Integer, nullable=False)
    unit_price = db.Column(db.Numeric(12, 2), nullable=False)
    total_amount = db.Column(db.Numeric(14, 2), nullable=False)
    created_at = db.Column(db.DateTime, default=_utcnow, index=True)

    def __repr__(self) -> str:
        return f"<Sale #{self.id} product={self.product_id} qty={self.quantity}>"
