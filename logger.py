"""Helper for writing audit logs."""
from flask_login import current_user
from app import db
from app.models import ActivityLog


def log_activity(
    action: str,
    description: str = "",
    product_id: int | None = None,
    previous_value=None,
    new_value=None,
) -> None:
    """
    Write one row to activity_logs.
    Safe to call outside a request context (user_id will be None).
    """
    try:
        uid = current_user.id if current_user and current_user.is_authenticated else None
    except RuntimeError:
        # Outside request context (e.g. CLI seed command)
        uid = None

    log = ActivityLog(
        user_id=uid,
        action=action,
        product_id=product_id,
        previous_value=str(previous_value) if previous_value is not None else None,
        new_value=str(new_value) if new_value is not None else None,
        description=description,
    )
    db.session.add(log)
