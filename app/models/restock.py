"""Restock log model."""
from datetime import datetime
from app import db


class Restock(db.Model):
    __tablename__ = "restocks"

    id = db.Column(db.Integer, primary_key=True)
    product_id = db.Column(db.Integer, db.ForeignKey("products.id"), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    previous_stock = db.Column(db.Integer, nullable=False)
    quantity_added = db.Column(db.Integer, nullable=False)
    updated_stock = db.Column(db.Integer, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, index=True)

    def __repr__(self) -> str:
        return f"<Restock #{self.id} product={self.product_id} +{self.quantity_added}>"
