"""Dynamic custom fields — no schema change required to add new fields."""
from datetime import datetime, timezone
from app import db

FIELD_TYPES = ("text", "number", "date", "boolean")


def _utcnow():
    return datetime.now(timezone.utc).replace(tzinfo=None)


class CustomField(db.Model):
    __tablename__ = "custom_fields"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), unique=True, nullable=False)
    label = db.Column(db.String(120), nullable=False)
    field_type = db.Column(db.String(20), nullable=False, default="text")
    is_visible = db.Column(db.Boolean, default=True, nullable=False)
    sort_order = db.Column(db.Integer, default=0, nullable=False)
    created_at = db.Column(db.DateTime, default=_utcnow)

    values = db.relationship("ProductCustomValue", backref="field",
                             lazy="dynamic", cascade="all, delete-orphan")


class ProductCustomValue(db.Model):
    __tablename__ = "product_custom_values"

    id = db.Column(db.Integer, primary_key=True)
    product_id = db.Column(db.Integer, db.ForeignKey("products.id"), nullable=False)
    field_id = db.Column(db.Integer, db.ForeignKey("custom_fields.id"), nullable=False)
    value = db.Column(db.Text)

    __table_args__ = (
        db.UniqueConstraint("product_id", "field_id", name="uq_product_field"),
    )
