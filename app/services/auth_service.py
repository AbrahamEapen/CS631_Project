from app.extensions import db
from app.models.updated_models import User
from werkzeug.security import generate_password_hash, check_password_hash
from flask_jwt_extended import create_access_token


def register_user(username, password):
    if not username or not password:
        return None, "Missing fields"

    existing = User.query.filter_by(username=username).first()
    if existing:
        return None, "User already exists"

    user = User(
        username=username,
        password=generate_password_hash(password),
        role="user"
    )

    db.session.add(user)
    db.session.commit()

    return user, None


def authenticate(username, password):
    user = User.query.filter_by(username=username).first()

    if not user:
        return None, "Invalid credentials"

    if not check_password_hash(user.password, password):
        return None, "Invalid credentials"

    token = create_access_token(identity=user.user_id)

    return token, None