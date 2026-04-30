from app.extensions import db
from app.models.updated_models import Account, Transaction


def deposit(account_id, amount):
    account = Account.query.get(account_id)
    if not account or amount <= 0:
        return None, "Invalid request"

    account.balance += amount
    tx = Transaction(account_number=account_id, amount=amount, code="DEP")
    db.session.add(tx)
    db.session.commit()
    return tx, None


def withdraw(account_id, amount):
    account = Account.query.get(account_id)
    if not account or amount <= 0:
        return None, "Invalid request"
    if account.balance < amount:
        return None, "Insufficient funds"

    account.balance -= amount
    tx = Transaction(account_number=account_id, amount=amount, code="WIT")
    db.session.add(tx)
    db.session.commit()
    return tx, None


def get_transactions(account_id):
    return Transaction.query.filter_by(account_number=account_id).all()