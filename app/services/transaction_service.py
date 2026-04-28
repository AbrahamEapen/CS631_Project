from app.extensions import db
from app.models.updated_models import Account, BankTransaction

def deposit(account_id, amount):
    account = Account.query.get(account_id)

    if not account or amount <= 0:
        return None, "Invalid request"

    account.balance += amount

    tx = Transaction(
        account_id=account_id,
        amount=amount,
        type="deposit"
    )

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

    tx = Transaction(
        account_id=account_id,
        amount=amount,
        type="withdraw"
    )

    db.session.add(tx)
    db.session.commit()

    return tx, None


def get_transactions(account_id):
    return Transaction.query.filter_by(account_id=account_id).all()