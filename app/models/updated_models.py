from datetime import datetime
from app.extensions import db


# =========================
# USER
# =========================
class User(db.Model):
    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=True)
    password = db.Column(db.String(255), nullable=False)
    role = db.Column(db.String(20), default="customer")
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    customer = db.relationship("Customer", back_populates="user", uselist=False)


# =========================
# BRANCH
# =========================
class Branch(db.Model):
    __tablename__ = "branch"

    branch_id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    city = db.Column(db.String(50), nullable=False)
    address = db.Column(db.String(200), nullable=False)
    assets = db.Column(db.Numeric, nullable=False)

    manager_ssn = db.Column(db.String(11), db.ForeignKey("employee.ssn", ondelete="SET NULL", use_alter=True, name="fk_branch_manager"), nullable=True)
    assistant_manager_ssn = db.Column(db.String(11), db.ForeignKey("employee.ssn", ondelete="SET NULL", use_alter=True, name="fk_branch_assistant_manager"), nullable=True)

    employees = db.relationship("Employee", back_populates="branch", foreign_keys="Employee.branch_id", cascade="all, delete")
    customers = db.relationship("Customer", back_populates="branch", cascade="all, delete")
    loan_accounts = db.relationship("LoanAccount", back_populates="branch")

    manager = db.relationship("Employee", foreign_keys=[manager_ssn], post_update=True)
    assistant_manager = db.relationship("Employee", foreign_keys=[assistant_manager_ssn], post_update=True)


# =========================
# EMPLOYEE
# =========================
class Employee(db.Model):
    __tablename__ = "employee"

    ssn = db.Column(db.String(11), primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    phone_number = db.Column(db.String(20), nullable=True)
    start_date = db.Column(db.Date, nullable=False)

    branch_id = db.Column(db.Integer, db.ForeignKey("branch.branch_id"), nullable=False)
    manager_ssn = db.Column(db.String(11), db.ForeignKey("employee.ssn", ondelete="SET NULL"), nullable=True)

    branch = db.relationship("Branch", back_populates="employees", foreign_keys=[branch_id])
    manager = db.relationship("Employee", remote_side=[ssn])
    dependents = db.relationship("EmployeeDependent", back_populates="employee", cascade="all, delete")
    customers = db.relationship("Customer", back_populates="personal_banker")


# =========================
# EMPLOYEE_DEPENDENT (Weak Entity)
# =========================
class EmployeeDependent(db.Model):
    __tablename__ = "employee_dependent"

    emp_ssn = db.Column(db.String(11), db.ForeignKey("employee.ssn", ondelete="CASCADE"), primary_key=True)
    dependent_name = db.Column(db.String(100), primary_key=True)

    employee = db.relationship("Employee", back_populates="dependents")


# =========================
# CUSTOMER
# =========================
class Customer(db.Model):
    __tablename__ = "customer"

    ssn = db.Column(db.String(11), primary_key=True)
    name = db.Column(db.String(100), nullable=False)

    apartment_no = db.Column(db.String(10))
    street_no = db.Column(db.String(10), nullable=False)
    city = db.Column(db.String(50), nullable=False)
    state = db.Column(db.String(50), nullable=False)
    zip_code = db.Column(db.String(10), nullable=False)

    branch_id = db.Column(db.Integer, db.ForeignKey("branch.branch_id"), nullable=False)
    personal_banker_ssn = db.Column(db.String(11), db.ForeignKey("employee.ssn", ondelete="SET NULL"), nullable=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=True)

    branch = db.relationship("Branch", back_populates="customers")
    personal_banker = db.relationship("Employee", back_populates="customers")
    account_links = db.relationship("CustomerAccount", back_populates="customer", cascade="all, delete")
    user = db.relationship("User", back_populates="customer")


# =========================
# ACCOUNT (Supertype)
# =========================
class Account(db.Model):
    __tablename__ = "account"

    account_number = db.Column(db.Integer, primary_key=True, autoincrement=True)
    balance = db.Column(db.Numeric(15, 2), nullable=False)
    account_type = db.Column(db.String(50), nullable=False)

    customer_links = db.relationship("CustomerAccount", back_populates="account", cascade="all, delete")
    transactions = db.relationship("BankTransaction", back_populates="account", cascade="all, delete")

    savings_detail = db.relationship("SavingsAccount", uselist=False, back_populates="account", cascade="all, delete")
    checking_detail = db.relationship("CheckingAccount", uselist=False, back_populates="account", cascade="all, delete")
    money_market_detail = db.relationship("MoneyMarketAccount", uselist=False, back_populates="account", cascade="all, delete")
    loan_detail = db.relationship("LoanAccount", uselist=False, back_populates="account", cascade="all, delete")


# =========================
# SUBTYPES
# =========================
class SavingsAccount(db.Model):
    __tablename__ = "savings_account"
    account_number = db.Column(db.Integer, db.ForeignKey("account.account_number", ondelete="CASCADE"), primary_key=True)
    interest_rate = db.Column(db.Numeric(5, 2), nullable=False)
    account = db.relationship("Account", back_populates="savings_detail")


class CheckingAccount(db.Model):
    __tablename__ = "checking_account"
    account_number = db.Column(db.Integer, db.ForeignKey("account.account_number", ondelete="CASCADE"), primary_key=True)
    overdraft_amount = db.Column(db.Numeric(15, 2), nullable=False)
    account = db.relationship("Account", back_populates="checking_detail")


class MoneyMarketAccount(db.Model):
    __tablename__ = "money_market_account"
    account_number = db.Column(db.Integer, db.ForeignKey("account.account_number", ondelete="CASCADE"), primary_key=True)
    variable_interest_rate = db.Column(db.Numeric(5, 2), nullable=False)
    account = db.relationship("Account", back_populates="money_market_detail")


class LoanAccount(db.Model):
    __tablename__ = "loan_account"
    account_number = db.Column(db.Integer, db.ForeignKey("account.account_number", ondelete="CASCADE"), primary_key=True)
    interest_rate = db.Column(db.Numeric(5, 2), nullable=False)
    monthly_payment = db.Column(db.Numeric(15, 2))
    branch_id = db.Column(db.Integer, db.ForeignKey("branch.branch_id"))
    account = db.relationship("Account", back_populates="loan_detail")
    branch = db.relationship("Branch", back_populates="loan_accounts")


# =========================
# CUSTOMER_ACCOUNT (Holds)
# =========================
class CustomerAccount(db.Model):
    __tablename__ = "customer_account"
    customer_ssn = db.Column(db.String(11), db.ForeignKey("customer.ssn", ondelete="CASCADE"), primary_key=True)
    account_number = db.Column(db.Integer, db.ForeignKey("account.account_number", ondelete="CASCADE"), primary_key=True)
    last_accessed_date = db.Column(db.Date)
    customer = db.relationship("Customer", back_populates="account_links")
    account = db.relationship("Account", back_populates="customer_links")


# =========================
# TRANSACTION TYPE
# =========================
class TransactionType(db.Model):
    __tablename__ = "transaction_type"
    code = db.Column(db.String(10), primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    is_chargeable = db.Column(db.Boolean, nullable=False)
    transactions = db.relationship("BankTransaction", back_populates="transaction_type", cascade="all, delete")


# =========================
# BANK TRANSACTION
# =========================
class BankTransaction(db.Model):
    __tablename__ = "bank_transaction"

    transaction_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    code = db.Column(db.String(10), db.ForeignKey("transaction_type.code", ondelete="CASCADE"), nullable=False)
    account_number = db.Column(db.Integer, db.ForeignKey("account.account_number", ondelete="CASCADE"), nullable=False)
    transaction_date = db.Column(db.Date, nullable=False, default=datetime.utcnow)
    transaction_hour = db.Column(db.Integer, nullable=False, default=0)
    amount = db.Column(db.Numeric(15, 2), nullable=False)

    transaction_type = db.relationship("TransactionType", back_populates="transactions")
    account = db.relationship("Account", back_populates="transactions")
