from flask import Blueprint, jsonify, request
from flask_jwt_extended import get_jwt_identity, jwt_required

from .service import summarize_user_activity


analytics_bp = Blueprint("analytics", __name__)


@analytics_bp.get("/activity")
@jwt_required()
def activity_analytics():
    raw_days = request.args.get("days", "30")
    try:
        days = int(raw_days)
    except ValueError:
        return jsonify({"error": "days must be an integer between 1 and 365."}), 400

    if not 1 <= days <= 365:
        return jsonify({"error": "days must be an integer between 1 and 365."}), 400

    summary = summarize_user_activity(int(get_jwt_identity()), days=days)
    return jsonify(summary), 200