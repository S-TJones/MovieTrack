from flask import Blueprint, g, request
from flask_jwt_extended import create_access_token, get_jwt_identity, jwt_required

from ..audit.actions import AuditAction
from ..audit.service import create_audit_event
from ..extensions import bcrypt, db
from ..models.users import User


auth_bp = Blueprint("auth", __name__)

# Registration endpoint
@auth_bp.post("/register")
def register():
    data = request.get_json(silent=True) or {}

    email = data.get("email", "").strip().lower()
    password = data.get("password", "")

    if not email or not password:
        return {
            "error": "Email and password are required."
        }, 400

    if len(password) < 8:
        return {
            "error": "Password must be at least 8 characters."
        }, 400

    existing_user = User.query.filter_by(email=email).first()

    if existing_user:
        return {
            "error": "Unable to create account with those details."
        }, 409

    password_hash = bcrypt.generate_password_hash(password).decode("utf-8")

    user = User(
        email=email,
        password_hash=password_hash,
    )

    db.session.add(user)
    db.session.flush()
    create_audit_event(
        user_id=user.id,
        action=AuditAction.USER_REGISTERED,
        resource_type="user",
        resource_id=user.id,
        correlation_id=g.correlation_id,
    )
    db.session.commit()

    access_token = create_access_token(identity=str(user.id))

    return {
        "message": "Account created successfully.",
        "access_token": access_token,
        "user": {
            "id": user.id,
            "email": user.email,
        },
    }, 201

# Login endpoint
@auth_bp.post("/login")
def login():
    data = request.get_json(silent=True) or {}

    email = data.get("email", "").strip().lower()
    password = data.get("password", "")

    if not email or not password:
        return {
            "error": "Email and password are required."
        }, 400

    user = User.query.filter_by(email=email).first()

    if not user or not bcrypt.check_password_hash(
        user.password_hash,
        password,
    ):
        create_audit_event(
            user_id=user.id if user else None,
            action=AuditAction.LOGIN_FAILED,
            resource_type="user",
            resource_id=user.id if user else None,
            correlation_id=g.correlation_id,
        )
        db.session.commit()
        return {
            "error": "Invalid email or password."
        }, 401

    create_audit_event(
        user_id=user.id,
        action=AuditAction.LOGIN_SUCCESS,
        resource_type="user",
        resource_id=user.id,
        correlation_id=g.correlation_id,
    )
    db.session.commit()

    access_token = create_access_token(identity=str(user.id))

    return {
        "access_token": access_token,
        "user": {
            "id": user.id,
            "email": user.email,
        },
    }, 200

# Get current user endpoint
@auth_bp.get("/me")
@jwt_required()
def get_current_user():
    user_id = get_jwt_identity()

    user = User.query.get(user_id)

    if not user:
        return {
            "error": "User not found."
        }, 404

    return {
        "id": user.id,
        "email": user.email,
    }, 200