from flask import Blueprint, request, jsonify
from app.models.updated_models import Account, Customer, CustomerAccount, User, Branch, SavingsAccount, CheckingAccount, MoneyMarketAccount
from app.extensions import db
import datetime

accounts_bp = Blueprint("accounts", __name__)


@accounts_bp.route("/search", methods=["GET"])
def search_accounts():
    """Search accounts by account number, type, or customer name."""
    q = request.args.get("q", "").strip()
    account_type = request.args.get("type", "").strip()

    query = Account.query

    if account_type:
        query = query.filter(Account.account_type.ilike(f"%{account_type}%"))

    if q:
        if q.isdigit():
            query = query.filter(Account.account_number == int(q))
        else:
            query = query.join(CustomerAccount, Account.account_number == CustomerAccount.account_number)\
                         .join(Customer, CustomerAccount.customer_ssn == Customer.ssn)\
                         .filter(Customer.name.ilike(f"%{q}%"))

    accounts = query.limit(50).all()

    return jsonify([
        {
            "account_number": a.account_number,
            "balance": float(a.balance),
            "account_type": a.account_type,
        }
        for a in accounts
    ]), 200


@accounts_bp.route("/customer/<string:customer_ssn>", methods=["GET"])
def accounts_by_customer(customer_ssn):
    """Get all accounts for a given customer SSN."""
    customer = Customer.query.get(customer_ssn)
    if not customer:
        return jsonify({"error": "Customer not found"}), 404

    accounts = [
        {
            "account_number": link.account.account_number,
            "balance": float(link.account.balance),
            "account_type": link.account.account_type,
        }
        for link in customer.account_links
    ]
    return jsonify(accounts), 200


@accounts_bp.route("/user/<int:user_id>", methods=["GET"])
def accounts_by_user(user_id):
    """Get all accounts for a given user by matching email to customer lookup."""
    user = User.query.get(user_id)
    if not user:
        return jsonify({"error": "User not found"}), 404

    customer = Customer.query.filter_by(
        ssn=None  # no direct FK — look up by email match
    ).first()

    # Since user_id FK was removed from Customer per the relational schema,
    # the frontend should use /accounts/customer/<ssn> instead.
    return jsonify({"error": "Use /accounts/customer/<ssn> to fetch accounts by customer"}), 400


@accounts_bp.route("/", methods=["POST"])
def create_account():
    data = request.get_json()
    if not data:
        return jsonify({"error": "Invalid payload"}), 400

    customer_ssn = data.get("customer_ssn")
    branch_id = data.get("branch_id")

    if not customer_ssn or not branch_id:
        return jsonify({"error": "Missing required fields"}), 400

    customer = Customer.query.get(customer_ssn)
    if not customer:
        return jsonify({"error": "Customer not found"}), 404

    account = Account(
        account_type=data.get("account_type", "savings"),
        balance=0.0
    )
    db.session.add(account)
    db.session.flush()

    link = CustomerAccount(customer_ssn=customer_ssn, account_number=account.account_number)
    db.session.add(link)
    db.session.commit()

    return jsonify({"message": "Account created", "account_number": account.account_number}), 201


@accounts_bp.route("/", methods=["GET"])
def get_accounts():
    accounts = Account.query.all()
    return jsonify([
        {
            "account_number": a.account_number,
            "balance": float(a.balance),
            "account_type": a.account_type
        }
        for a in accounts
    ]), 200


@accounts_bp.route("/profile/<int:user_id>", methods=["GET"])
def get_profile(user_id):
    user = User.query.get(user_id)
    if not user:
        return jsonify({"error": "User not found"}), 404

    # user_id FK removed from Customer per schema — no direct relationship
    return jsonify({
        "user_id": user.id,
        "username": user.username,
        "email": user.email,
        "role": user.role,
        "created_at": user.created_at.isoformat() if user.created_at else None,
        "customer_name": None,
        "accounts": []
    }), 200


@accounts_bp.route("/create", methods=["POST"])
def create_account_for_user():
    data = request.get_json()
    customer_ssn = data.get("customer_ssn")
    account_type = data.get("account_type", "savings")

    if not customer_ssn:
        return jsonify({"error": "customer_ssn is required"}), 400

    customer = Customer.query.get(customer_ssn)
    if not customer:
        return jsonify({"error": "Customer not found"}), 404

    account = Account(balance=0.00, account_type=account_type)
    db.session.add(account)
    db.session.flush()

    if account_type == "savings":
        db.session.add(SavingsAccount(account_number=account.account_number, interest_rate=0.035))
    elif account_type == "checking":
        db.session.add(CheckingAccount(account_number=account.account_number, overdraft_amount=200.00))
    elif account_type == "money_market":
        db.session.add(MoneyMarketAccount(account_number=account.account_number, variable_interest_rate=0.052))

    db.session.add(CustomerAccount(
        customer_ssn=customer.ssn,
        account_number=account.account_number,
        last_access_date=datetime.date.today()
    ))
    db.session.commit()

    return jsonify({
        "message": "Account created successfully",
        "account_number": account.account_number,
        "account_type": account_type,
        "balance": 0.00
    }), 201