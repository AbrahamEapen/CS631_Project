"""
seed.py — Populate the CS631 banking database with realistic sample data.

Seed user (regular account):
  Email:    john.doe@example.com
  Password: password123

Admin account:
  Email:    admin@bank.com
  Password: admin123

Run:
  python seed.py
"""

import random
from datetime import datetime, timedelta, date
from faker import Faker
from werkzeug.security import generate_password_hash
import psycopg2
def _hash(pw):
    return generate_password_hash(pw, method="pbkdf2:sha256", salt_length=8)

from app import create_app
from app.extensions import db
from app.models.updated_models import (
    User, Customer, Account, BankTransaction, Branch, Employee,
    TransactionType, CustomerAccount, EmployeeDependent,
    SavingsAccount, CheckingAccount, MoneyMarketAccount, LoanAccount,
)

fake = Faker()
random.seed(42)
Faker.seed(42)

app = create_app()

NUM_BRANCHES    = 3
NUM_EMPLOYEES   = 8
NUM_EXTRA_USERS = 9   # additional random users (seed user is +1, admin is +1)
NUM_TRANSACTIONS = 60


def _random_date(days_back=365):
    return date.today() - timedelta(days=random.randint(0, days_back))


def run_seed():
    with app.app_context():
        print("Dropping and recreating all tables…")
# NEW
        import psycopg2
        db.engine.dispose()
        url = db.engine.url.render_as_string(hide_password=False)
        raw = psycopg2.connect(url)
        raw.autocommit = True
        cur = raw.cursor()
        cur.execute("SELECT schema_name FROM information_schema.schemata WHERE schema_name = 'public'")
        if cur.fetchone():
            cur.execute("DROP SCHEMA public CASCADE")
        cur.execute("CREATE SCHEMA public")
        cur.close()
        raw.close()
        db.create_all()
        # ── TRANSACTION TYPES ──────────────────────────────────────────────
        tx_types = [
            TransactionType(code="DEP", name="Deposit",    is_chargeable=False),
            TransactionType(code="WIT", name="Withdrawal", is_chargeable=True),
            TransactionType(code="TRF", name="Transfer",   is_chargeable=False),
        ]
        db.session.add_all(tx_types)
        db.session.commit()
        print("  ✓ Transaction types")

        # ── BRANCHES ───────────────────────────────────────────────────────
        branch_data = [
            ("Midtown Main Branch",   "New York",    "100 Park Ave, New York, NY 10017",       8_500_000),
            ("Westside Branch",       "Los Angeles", "456 Sunset Blvd, Los Angeles, CA 90028", 5_200_000),
            ("South Loop Branch",     "Chicago",     "200 S Wacker Dr, Chicago, IL 60606",     3_900_000),
        ]
        branches = []
        for i, (name, city, address, assets) in enumerate(branch_data):
            b = Branch(branch_id=i+1, name=name, city=city, address=address, assets=assets)
            db.session.add(b)
            branches.append(b)
        db.session.commit()
        print(f"  ✓ {len(branches)} branches")

        # ── EMPLOYEES ─────────────────────────────────────────────────────
        employees = []

        # Head manager
        head_mgr = Employee(
            ssn="100-00-0001",
            name="Patricia Reynolds",
            phone_number="212-555-0100",
            start_date=date(2015, 3, 1),
            branch_id=branches[0].branch_id,
            manager_ssn=None,
        )
        db.session.add(head_mgr)
        db.session.flush()
        employees.append(head_mgr)

        for i in range(NUM_EMPLOYEES - 1):
            ssn = f"200-00-{i+1:04d}"
            emp = Employee(
                ssn=ssn,
                name=fake.name(),
                phone_number=fake.phone_number()[:20],
                start_date=_random_date(days_back=3000),
                branch_id=random.choice(branches).branch_id,
                manager_ssn=head_mgr.ssn,
            )
            db.session.add(emp)
            employees.append(emp)

        db.session.commit()

        # Assign managers to branches
        for i, branch in enumerate(branches):
            branch.manager_ssn = head_mgr.ssn
            branch.assistant_manager_ssn = employees[i + 1].ssn
        db.session.commit()
        print(f"  ✓ {len(employees)} employees")

        # ── EMPLOYEE DEPENDENTS ────────────────────────────────────────────
        for emp in employees:
            for _ in range(random.randint(0, 2)):
                db.session.add(EmployeeDependent(emp_ssn=emp.ssn, dependent_name=fake.name()))
        db.session.commit()
        print("  ✓ Employee dependents")

        # ── HELPER: create an account with subtype ─────────────────────────
        def make_account(acc_type=None):
            acc_type = acc_type or random.choice(["savings", "checking", "money_market", "loan"])
            balance = round(random.uniform(250, 15000), 2)
            acc = Account(balance=balance, account_type=acc_type)
            db.session.add(acc)
            db.session.flush()

            if acc_type == "savings":
                db.session.add(SavingsAccount(account_number=acc.account_number,
                                              interest_rate=round(random.uniform(0.01, 0.05), 4)))
            elif acc_type == "checking":
                db.session.add(CheckingAccount(account_number=acc.account_number,
                                               overdraft_amount=round(random.uniform(0, 500), 2)))
            elif acc_type == "money_market":
                db.session.add(MoneyMarketAccount(account_number=acc.account_number,
                                                  variable_interest_rate=round(random.uniform(0.01, 0.07), 4)))
            elif acc_type == "loan":
                db.session.add(LoanAccount(account_number=acc.account_number,
                                           interest_rate=round(random.uniform(0.03, 0.12), 4),
                                           monthly_payment=round(random.uniform(100, 1200), 2),
                                           branch_id=random.choice(branches).branch_id))
            return acc

        all_accounts = []

        # ── SEED USER (known credentials) ─────────────────────────────────
        seed_user = User(
            username="john.doe@example.com",
            email="john.doe@example.com",
            password=_hash("password123"),
            role="customer",
        )
        db.session.add(seed_user)
        db.session.flush()

        seed_customer = Customer(
            ssn="SEED-0001",
            name="John Doe",
            street_no="742",
            apartment_no="4B",
            city="New York",
            state="NY",
            zip_code="10001",
            branch_id=branches[0].branch_id,
            personal_banker_ssn=employees[1].ssn,
            user_id=seed_user.id,
        )
        db.session.add(seed_customer)
        db.session.flush()

        # Give seed user three accounts: savings, checking, and a money market
        seed_accounts = []
        for acc_type, balance in [("savings", 4250.00), ("checking", 1875.50), ("money_market", 9100.00)]:
            acc = Account(balance=balance, account_type=acc_type)
            db.session.add(acc)
            db.session.flush()

            if acc_type == "savings":
                db.session.add(SavingsAccount(account_number=acc.account_number, interest_rate=0.0350))
            elif acc_type == "checking":
                db.session.add(CheckingAccount(account_number=acc.account_number, overdraft_amount=200.00))
            elif acc_type == "money_market":
                db.session.add(MoneyMarketAccount(account_number=acc.account_number,
                                                  variable_interest_rate=0.0520))

            db.session.add(CustomerAccount(
                customer_ssn=seed_customer.ssn,
                account_number=acc.account_number,
                last_accessed_date=date.today() - timedelta(days=1),
            ))
            seed_accounts.append(acc)
            all_accounts.append(acc)

        db.session.commit()
        print(f"  ✓ Seed user: john.doe@example.com / password123  (3 accounts)")

        # ── RANDOM USERS + CUSTOMERS + ACCOUNTS ───────────────────────────
        for i in range(NUM_EXTRA_USERS):
            email = f"user{i}@example.com"
            user = User(
                username=email,
                email=email,
                password=_hash("password123"),
                role="customer",
            )
            db.session.add(user)
            db.session.flush()

            ssn = f"RAND-{i+1:04d}"
            customer = Customer(
                ssn=ssn,
                name=fake.name(),
                street_no=str(random.randint(1, 999)),
                apartment_no=str(random.randint(1, 50)) if random.random() > 0.4 else None,
                city=fake.city(),
                state=fake.state_abbr(),
                zip_code=fake.zipcode(),
                branch_id=random.choice(branches).branch_id,
                personal_banker_ssn=random.choice(employees).ssn,
                user_id=user.id,
            )
            db.session.add(customer)
            db.session.flush()

            # 1 or 2 accounts per random user
            for _ in range(random.randint(1, 2)):
                acc = make_account()
                db.session.add(CustomerAccount(
                    customer_ssn=customer.ssn,
                    account_number=acc.account_number,
                    last_accessed_date=_random_date(days_back=60),
                ))
                all_accounts.append(acc)

        db.session.commit()
        print(f"  ✓ {NUM_EXTRA_USERS} random users with accounts")

        # ── ADMIN USER ────────────────────────────────────────────────────
        admin = User(
            username="admin@bank.com",
            email="admin@bank.com",
            password=_hash("admin123"),
            role="admin",
        )
        db.session.add(admin)
        db.session.commit()
        print("  ✓ Admin user: admin@bank.com / admin123")

        # ── TRANSACTIONS ─────────────────────────────────────────────────
        # Rich history for seed user accounts
        seed_tx_history = [
            ("DEP", seed_accounts[0], 1200.00, 45),
            ("DEP", seed_accounts[0],  500.00, 30),
            ("WIT", seed_accounts[0],  250.00, 25),
            ("DEP", seed_accounts[0],  800.00, 15),
            ("WIT", seed_accounts[0],  100.00,  7),
            ("DEP", seed_accounts[1], 2000.00, 60),
            ("WIT", seed_accounts[1],  350.00, 45),
            ("TRF", seed_accounts[1],  500.00, 20),
            ("DEP", seed_accounts[1],  750.00, 10),
            ("DEP", seed_accounts[2], 5000.00, 90),
            ("DEP", seed_accounts[2], 4000.00, 45),
            ("WIT", seed_accounts[2],  200.00, 14),
        ]
        for code, acc, amount, days_ago in seed_tx_history:
            db.session.add(BankTransaction(
                code=code,
                account_number=acc.account_number,
                transaction_date=date.today() - timedelta(days=days_ago),
                transaction_hour=random.randint(8, 17),
                amount=amount,
            ))

        # Random transactions for all accounts
        for _ in range(NUM_TRANSACTIONS):
            acc = random.choice(all_accounts)
            code = random.choice(["DEP", "WIT", "TRF"])
            db.session.add(BankTransaction(
                code=code,
                account_number=acc.account_number,
                transaction_date=_random_date(days_back=180),
                transaction_hour=random.randint(0, 23),
                amount=round(random.uniform(10, 2000), 2),
            ))

        db.session.commit()
        print(f"  ✓ {len(seed_tx_history) + NUM_TRANSACTIONS} transactions")

        print("\n✅ Seeding complete!")
        print("─" * 40)
        print("  Seed user : john.doe@example.com / password123")
        print("  Admin     : admin@bank.com / admin123")
        print("─" * 40)


if __name__ == "__main__":
    run_seed()