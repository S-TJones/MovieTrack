
from datetime import datetime, timezone
from ..extensions import db

class AuditEvent(db.Model):
    __tablename__ = "audit_events"

    id = db.Column(
        db.BigInteger().with_variant(db.Integer, "sqlite"),
        primary_key=True,
    )

    user_id = db.Column(
        db.Integer,
        db.ForeignKey("users.id", ondelete="SET NULL"),
        nullable=True,
    )

    action = db.Column(
        db.String(100),
        nullable=False,
    )

    resource_type = db.Column(
        db.String(100),
        nullable=False,
    )

    resource_id = db.Column(
        db.String(100),
        nullable=True,
    )

    correlation_id = db.Column(
        db.String(100),
        nullable=False,
        index=True,
    )

    metadata_json = db.Column(
        db.JSON,
        nullable=True,
    )

    created_at = db.Column(
        db.DateTime(timezone=True),
        nullable=False,
        default=lambda: datetime.now(timezone.utc),
        index=True,
    )