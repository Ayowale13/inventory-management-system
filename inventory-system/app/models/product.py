"""Product model — core inventory record."""
from datetime import datetime
from app import db


class Product(db.Model):
    __tablename__ = "products"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(150), nullable=False, index=True)
    category = db.Column(db.String(80), index=True)
    cost_price = db.Column(db.Numeric(12, 2), default=0, nullable=False)
    selling_price = db.Column(db.Numeric(12, 2), default=0, nullable=False)
    quantity = db.Column(db.Integer, default=0, nullable=False)
    min_stock = db.Column(db.Integer, default=5, nullable=False)
    date_added = db.Column(db.DateTime, default=datetime.utcnow)
    last_updated = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    sales = db.relationship("Sale", backref="product", lazy="dynamic",
                            cascade="all, delete-orphan")
    restocks = db.relationship("Restock", backref="product", lazy="dynamic",
                               cascade="all, delete-orphan")
    custom_values = db.relationship("ProductCustomValue", backref="product",
                                    lazy="dynamic", cascade="all, delete-orphan")

    @property
    def is_low_stock(self) -> bool:
        return 0 < self.quantity <= self.min_stock

    @property
    def is_out_of_stock(self) -> bool:
        return self.quantity <= 0

    @property
    def stock_status(self) -> str:
        if self.is_out_of_stock:
            return "Out of Stock"
        if self.is_low_stock:
            return "Low Stock"
        return "In Stock"

    def __repr__(self) -> str:
        return f"<Product {self.name} qty={self.quantity}>"
