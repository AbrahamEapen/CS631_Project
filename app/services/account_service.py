from app.extensions import db
from app.models.updated_models import Account
from app.models.updated_models import Customer


# GET USER ACCOUNTS
def get_user_accounts(customer_id):
    return Account.query.filter_by(customer_id=customer_id).all()


# GET SINGLE ACCOUNT
def get_account(account_id):
    return Account.query.get(account_id)


# CREATE ACCOUNT
def create_account(customer_id, branch_id, account_type="savings"):
    # validate customer exists
    customer = Customer.query.get(customer_id)
    if not customer:
        return None

    account = Account(
        customer_id=customer_id,
        branch_id=branch_id,
        account_type=account_type,
        balance=0.0
    )

    db.session.add(account)
    db.session.commit()
    return account


# DELETE ACCOUNT
def delete_account(account_id):
    account = Account.query.get(account_id)
    if not account:
        return False

    db.session.delete(account)
    db.session.commit()
    return True