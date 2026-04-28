from flask import Blueprint, jsonify, session, render_template, redirect, url_for, flash
from app.models.updated_models import User, BankTransaction, Account

admin_bp = Blueprint("admin", __name__)


def _is_admin():
    return session.get("role") == "admin"


# ── Pages ────────────────────────────────────────────────────────────────

@admin_bp.route("/dashboard")
def dashboard_page():
    if not _is_admin():
        flash("Admin access required", "error")
        return redirect(url_for("main.home"))
    return render_template("admin/dashboard.html", username=session.get("username"))

@admin_bp.route("/users")
def users_page():
    if not _is_admin():
        flash("Admin access required", "error")
        return redirect(url_for("main.home"))
    return render_template("admin/users.html", username=session.get("username"))

@admin_bp.route("/transactions")
def transactions_page():
    if not _is_admin():
        flash("Admin access required", "error")
        return redirect(url_for("main.home"))
    return render_template("admin/transactions.html", username=session.get("username"))


# ── API ──────────────────────────────────────────────────────────────────

@admin_bp.route("/api/stats")
def stats():
    if not _is_admin():
        return jsonify({"error": "Forbidden"}), 403
    return jsonify({
        "total_users": User.query.count(),
        "total_transactions": BankTransaction.query.count(),
        "total_accounts": Account.query.count(),
    }), 200

@admin_bp.route("/api/users")
def all_users():
    if not _is_admin():
        return jsonify({"error": "Forbidden"}), 403
    return jsonify([
        {
            "id": u.id,
            "username": u.username,
            "email": u.email,
            "role": u.role,
            "created_at": u.created_at.isoformat() if u.created_at else None
        }
        for u in User.query.all()
    ]), 200

@admin_bp.route("/api/transactions")
def all_transactions():
    if not _is_admin():
        return jsonify({"error": "Forbidden"}), 403
    return jsonify([
        {
            "id": t.transaction_id,
            "account_number": t.account_number,
            "amount": float(t.amount),
            "type": t.code,
            "date": t.transaction_date.isoformat() if t.transaction_date else None,
        }
        for t in BankTransaction.query.order_by(BankTransaction.transaction_date.desc()).all()
    ]), 200