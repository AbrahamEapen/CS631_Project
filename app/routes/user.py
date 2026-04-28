from flask import Blueprint, jsonify, request

from app.services.account_service import (
    get_user_accounts,
    get_account,
    create_account,
    delete_account
)

user_bp = Blueprint("user_bp", __name__)


# GET USER ACCOUNTS
@user_bp.route("/<int:customer_id>/accounts", methods=["GET"])
def user_accounts(customer_id):
    accounts = get_user_accounts(customer_id)

    return jsonify([
        {
            "account_id": a.account_id,
            "customer_id": a.customer_id,
            "branch_id": a.branch_id,
            "balance": a.balance,
            "account_type": a.account_type
        }
        for a in accounts
    ]), 200


# GET SINGLE ACCOUNT
@user_bp.route("/account/<int:account_id>", methods=["GET"])
def user_account(account_id):
    account = get_account(account_id)

    if not account:
        return jsonify({"error": "Account not found"}), 404

    return jsonify({
        "account_id": account.account_id,
        "customer_id": account.customer_id,
        "branch_id": account.branch_id,
        "balance": account.balance,
        "account_type": account.account_type
    }), 200


# CREATE ACCOUNT
@user_bp.route("/account", methods=["POST"])
def user_create_account():
    data = request.get_json()

    account = create_account(
        customer_id=data.get("customer_id"),
        branch_id=data.get("branch_id"),
        account_type=data.get("account_type", "savings")
    )

    if not account:
        return jsonify({"error": "Invalid customer"}), 400

    return jsonify({
        "message": "Account created",
        "account_id": account.account_id
    }), 201


# DELETE ACCOUNT
@user_bp.route("/account/<int:account_id>", methods=["DELETE"])
def user_delete_account(account_id):
    success = delete_account(account_id)

    if not success:
        return jsonify({"error": "Account not found"}), 404

    return jsonify({"message": "Account deleted"}), 200