from flask import Blueprint, g, jsonify, request
from flask_jwt_extended import get_jwt_identity, jwt_required

from ..audit.actions import AuditAction
from ..audit.service import create_audit_event
from ..extensions import db
from ..movies.tmdb_service import TMDBError
from .service import AIService


ai_bp = Blueprint("ai", __name__)


@ai_bp.post("/search")
@jwt_required()
def ai_search():
	data = request.get_json(silent=True)
	query = data.get("query") if isinstance(data, dict) else None
	if not isinstance(query, str) or not query.strip():
		return jsonify({"error": "A search query is required."}), 400
	query = query.strip()
	if len(query) > 500:
		return jsonify({"error": "Search query is too long."}), 400

	create_audit_event(
		action=AuditAction.AI_SEARCH_REQUESTED,
		resource_type="ai_search",
		user_id=int(get_jwt_identity()),
		correlation_id=g.correlation_id,
	)
	db.session.commit()

	try:
		result = AIService().search(query)
	except (TMDBError, RuntimeError):
		return jsonify({"error": "Movie search is temporarily unavailable."}), 502

	return jsonify(result), 200


@ai_bp.post("/recommendations")
@jwt_required()
def ai_recommendations():
	user_id = int(get_jwt_identity())
	create_audit_event(
		action=AuditAction.AI_RECOMMENDATION_REQUESTED,
		resource_type="ai_recommendation",
		user_id=user_id,
		correlation_id=g.correlation_id,
	)
	db.session.commit()

	try:
		result = AIService().recommendations(user_id)
	except (TMDBError, RuntimeError):
		return jsonify({
			"error": "Recommendations are temporarily unavailable."
		}), 502

	return jsonify(result), 200
