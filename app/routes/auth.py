from flask import Blueprint, request, jsonify, session
from werkzeug.security import generate_password_hash, check_password_hash
from app.extensions import db
from app.models.updated_models import User

auth_bp = Blueprint("auth", __name__)


# -----------------------
# REGISTER
# -----------------------
@auth_bp.route("/register", methods=["POST"])
def register():
    data = request.get_json(silent=True) or request.form

    username = data.get("username") or data.get("email")
    email = data.get("email", username)
    password = data.get("password")
    role = data.get("role", "customer")

    if not username or not password:
        return jsonify({"error": "Missing credentials"}), 400

    existing_user = User.query.filter_by(username=username).first()
    if existing_user:
        return jsonify({"error": "User already exists"}), 400

    user = User(
        username=username,
        email=email,
        password=generate_password_hash(password),
        role=role
    )

    db.session.add(user)
    db.session.commit()
    db.session.refresh(user)

    return jsonify({
        "message": "User created successfully",
        "user_id": user.id
    }), 201


# -----------------------
# LOGIN
# -----------------------
@auth_bp.route("/login", methods=["POST"])
def login():
    data = request.get_json(silent=True)

    if not data:
        return jsonify({"error": "Missing JSON body"}), 400

    username = data.get("username")
    password = data.get("password")

    if not username or not password:
        return jsonify({"error": "Missing credentials"}), 400

    user = User.query.filter_by(username=username).first()

    if not user or not check_password_hash(user.password, password):
        return jsonify({"error": "Invalid credentials"}), 401

    return jsonify({
        "message": "Login successful",
        "token": f"test-token-{user.id}",
        "user_id": user.id,
        "role": user.role,
        "username": user.username,
        "email": user.email
    }), 200
