from flask import Blueprint, jsonify, session, render_template, redirect, url_for, flash
from app.models.updated_models import User, BankTransaction, Account, Customer, LoanAccount, CustomerAccount
from app.extensions import db

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

@admin_bp.route("/api/users/<int:user_id>", methods=["DELETE"])
def delete_user(user_id):
    if not _is_admin():
        return jsonify({"error": "Forbidden"}), 403

    user = User.query.get(user_id)
    if not user:
        return jsonify({"error": "User not found"}), 404

    customer = user.customer

    if customer:
        linked_account_numbers = [
            link.account_number for link in customer.account_links
        ]
        if linked_account_numbers:
            loan = (
                LoanAccount.query
                .filter(LoanAccount.account_number.in_(linked_account_numbers))
                .first()
            )
            if loan:
                return jsonify({
                    "error": (
                        f"Cannot delete customer '{customer.name}'. "
                        f"They have an active loan account "
                        f"(account #{loan.account_number}). "
                        "Close all loan accounts first."
                    )
                }), 409

    try:
        if customer:
            db.session.delete(customer)
        db.session.delete(user)
        db.session.commit()
        return jsonify({"message": "User deleted successfully"}), 200
    except ValueError as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 409
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": f"Deletion failed: {str(e)}"}), 500