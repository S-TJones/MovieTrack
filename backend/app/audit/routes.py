from flask import Blueprint, jsonify, request
from flask_jwt_extended import get_jwt_identity, jwt_required

from ..models import AuditEvent


audit_bp = Blueprint("audit", __name__)


@audit_bp.get("/history")
@jwt_required()
def get_audit_history():
	user_id = int(get_jwt_identity())
	try:
		limit = int(request.args.get("limit", 50))
	except ValueError:
		return jsonify({"error": "Limit must be an integer."}), 400

	limit = max(1, min(limit, 100))
	events = (
		AuditEvent.query
		.filter_by(user_id=user_id)
		.order_by(AuditEvent.created_at.desc(), AuditEvent.id.desc())
		.limit(limit + 1)
		.all()
	)
	has_more = len(events) > limit

	return jsonify({
		"items": [
			{
				"id": event.id,
				"action": event.action,
				"resource_type": event.resource_type,
				"resource_id": event.resource_id,
				"correlation_id": event.correlation_id,
				"metadata": event.metadata_json,
				"created_at": event.created_at.isoformat(),
			}
			for event in events[:limit]
		],
		"has_more": has_more,
	}), 200
