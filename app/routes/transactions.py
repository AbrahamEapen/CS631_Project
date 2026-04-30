from flask import Blueprint, request, jsonify
from datetime import date
from app.extensions import db
from app.models.updated_models import Account, Transaction, CustomerAccount, TransactionType

transactions_bp = Blueprint("transactions", __name__)


def _ensure_transaction_types():
    """Ensure basic transaction type codes exist."""
    for code, name in [("DEP", "Deposit"), ("WIT", "Withdrawal"), ("TRF", "Transfer")]:
        if not TransactionType.query.get(code):
            db.session.add(TransactionType(code=code, name=name, is_chargeable=False))
    db.session.commit()


@transactions_bp.route("/deposit", methods=["POST"])
def deposit_route():
    data = request.get_json()
    account_number = data.get("account_number") or data.get("account_id")
    amount = float(data.get("amount", 0))

    account = Account.query.get(account_number)
    if not account or amount <= 0:
        return jsonify({"error": "Invalid request"}), 400

    _ensure_transaction_types()
    account.balance = float(account.balance) + amount

    tx = Transaction(
        code="DEP",
        account_number=account_number,
        amount=amount,
        date=date.today(),
        hour=0
    )
    db.session.add(tx)
    db.session.commit()
    return jsonify({"transaction_id": tx.transaction_id, "new_balance": float(account.balance)}), 201


@transactions_bp.route("/withdraw", methods=["POST"])
def withdraw_route():
    data = request.get_json()
    account_number = data.get("account_number") or data.get("account_id")
    amount = float(data.get("amount", 0))

    account = Account.query.get(account_number)
    if not account or amount <= 0:
        return jsonify({"error": "Invalid request"}), 400
    if float(account.balance) < amount:
        return jsonify({"error": "Insufficient funds"}), 400

    _ensure_transaction_types()
    account.balance = float(account.balance) - amount

    tx = Transaction(
        code="WIT",
        account_number=account_number,
        amount=amount,
        date=date.today(),
        hour=0
    )
    db.session.add(tx)
    db.session.commit()
    return jsonify({"transaction_id": tx.transaction_id, "new_balance": float(account.balance)}), 201


@transactions_bp.route("/transfer", methods=["POST"])
def transfer_route():
    data = request.get_json()
    from_account_number = data.get("from_account_number")
    to_account_number = data.get("to_account_number")
    amount = float(data.get("amount", 0))

    from_account = Account.query.get(from_account_number)
    to_account = Account.query.get(to_account_number)

    if not from_account or not to_account or amount <= 0:
        return jsonify({"error": "Invalid request"}), 400
    if float(from_account.balance) < amount:
        return jsonify({"error": "Insufficient funds"}), 400
    if from_account_number == to_account_number:
        return jsonify({"error": "Cannot transfer to the same account"}), 400

    _ensure_transaction_types()
    from_account.balance = float(from_account.balance) - amount
    to_account.balance = float(to_account.balance) + amount

    tx_out = Transaction(code="TRF", account_number=from_account_number,
                         amount=amount, date=date.today(), hour=0)
    tx_in  = Transaction(code="TRF", account_number=to_account_number,
                         amount=amount, date=date.today(), hour=0)
    db.session.add_all([tx_out, tx_in])
    db.session.commit()
    return jsonify({
        "message": "Transfer successful",
        "debit_transaction_id": tx_out.transaction_id,
        "credit_transaction_id": tx_in.transaction_id
    }), 201


@transactions_bp.route("/<int:account_number>", methods=["GET"])
def list_transactions(account_number):
    txs = Transaction.query.filter_by(account_number=account_number).order_by(
        Transaction.date.desc()).all()
    return jsonify([
        {
            "id": t.transaction_id,
            "amount": float(t.amount),
            "type": t.code,
            "date": t.date.isoformat() if t.date else None
        } for t in txs
    ]), 200