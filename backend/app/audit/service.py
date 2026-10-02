import uuid
from datetime import datetime, timezone

from flask import g, has_request_context

from ..extensions import db
from ..models import AuditEvent
from .actions import AuditAction


def create_audit_event(
    *, action: AuditAction, resource_type,
    resource_id=None, user_id=None, correlation_id=None,
    metadata=None):
    
    action = AuditAction(action)
    if correlation_id is None and has_request_context():
        correlation_id = getattr(g, "correlation_id", None)

    event = AuditEvent(
        user_id=user_id,
        action=action.value,
        resource_type=resource_type,
        resource_id=str(resource_id) if resource_id is not None else None,
        correlation_id=correlation_id or str(uuid.uuid4()),
        metadata_json=metadata,
        created_at=datetime.now(timezone.utc),
    )

    db.session.add(event)

    return event