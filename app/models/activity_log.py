"""Audit trail."""
from datetime import datetime, timezone
from app import db


def _utcnow():
    return datetime.now(timezone.utc).replace(tzinfo=None)


class ActivityLog(db.Model):
    __tablename__ = "activity_logs"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"))
    action = db.Column(db.String(80), nullable=False)
    product_id = db.Column(db.Integer, db.ForeignKey("products.id"))
    previous_value = db.Column(db.Text)
    new_value = db.Column(db.Text)
    description = db.Column(db.String(255))
    created_at = db.Column(db.DateTime, default=_utcnow, index=True)

    product = db.relationship("Product")
