from flask import Blueprint, render_template, request, redirect, url_for, flash, session
import requests as http_requests
from werkzeug.security import check_password_hash, generate_password_hash
from app.extensions import db
from app.models.updated_models import User

main_bp = Blueprint("main", __name__, template_folder="../templates")


def _api_url(path):
    return f"http://127.0.0.1:5000/{path}"


# -----------------------
# Home (Login page)
# -----------------------
@main_bp.route("/", methods=["GET"])
def home():
    if session.get("user_id"):
        if session.get("role") == "admin":
            return redirect(url_for("main.admin_dashboard"))
        return redirect(url_for("main.dashboard"))
    return render_template("login.html")


# -----------------------
# LOGIN
# -----------------------
@main_bp.route("/login", methods=["POST"])
def login():
    username = request.form.get("email")
    password = request.form.get("password")

    user = User.query.filter_by(username=username).first()
    if not user or not check_password_hash(user.password, password):
        flash("Invalid credentials", "error")
        return redirect(url_for("main.home"))

    session["user_id"] = user.id
    session["username"] = user.username
    session["email"] = user.email or ""
    session["role"] = user.role
    session["token"] = f"test-token-{user.id}"

    if user.role == "admin":
        return redirect(url_for("main.admin_dashboard"))
    return redirect(url_for("main.dashboard"))


# -----------------------
# LOGOUT
# -----------------------
@main_bp.route("/logout")
def logout():
    session.clear()
    flash("Logged out successfully", "info")
    return redirect(url_for("main.home"))


# -----------------------
# REGISTER PAGE (GET)
# -----------------------
@main_bp.route("/register", methods=["GET"])
def register_page():
    return render_template("register.html")


# -----------------------
# REGISTER (POST)
# -----------------------
@main_bp.route("/register", methods=["POST"])
def register():
    email = request.form.get("email")
    password = request.form.get("password")

    if not email or not password:
        flash("Email and password are required", "error")
        return redirect(url_for("main.register_page"))

    if User.query.filter_by(username=email).first():
        flash("An account with that email already exists", "error")
        return redirect(url_for("main.register_page"))

    user = User(
        username=email,
        email=email,
        password=generate_password_hash(password, method="pbkdf2:sha256", salt_length=8),
        role="customer",
    )
    db.session.add(user)
    db.session.commit()
    flash("Registration successful! Please log in.", "success")
    return redirect(url_for("main.home"))


# -----------------------
# USER DASHBOARD
# -----------------------
@main_bp.route("/dashboard", methods=["GET"])
def dashboard():
    if not session.get("user_id"):
        flash("Please log in first", "error")
        return redirect(url_for("main.home"))
    return render_template("dashboard.html",
                           username=session.get("username"),
                           user_id=session.get("user_id"))


# -----------------------
# USER PROFILE
# -----------------------
@main_bp.route("/profile", methods=["GET"])
def profile():
    if not session.get("user_id"):
        flash("Please log in first", "error")
        return redirect(url_for("main.home"))
    return render_template("profile.html",
                           username=session.get("username"),
                           email=session.get("email"),
                           role=session.get("role"),
                           user_id=session.get("user_id"))


# -----------------------
# SEARCH PAGE
# -----------------------
@main_bp.route("/search", methods=["GET"])
def search():
    if not session.get("user_id"):
        flash("Please log in first", "error")
        return redirect(url_for("main.home"))
    query = request.args.get("q", "")
    return render_template("search.html",
                           username=session.get("username"),
                           query=query)


# -----------------------
# TRANSFER PAGE
# -----------------------
@main_bp.route("/transfer", methods=["GET"])
def transfer():
    if not session.get("user_id"):
        flash("Please log in first", "error")
        return redirect(url_for("main.home"))
    return render_template("transfer.html",
                           username=session.get("username"),
                           user_id=session.get("user_id"))

