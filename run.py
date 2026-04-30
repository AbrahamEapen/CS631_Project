"""
run.py — Start the CS631 Banking application.

Local development (SQLite):
  python run.py
  Auto-seeds on first launch if banking.db does not exist.

Docker (Postgres):
  Handled by entrypoint.sh — tables are created and seed runs before
  this file is executed via gunicorn.

Credentials after seeding:
  Seed user : john.doe@example.com / password123
  Admin     : admin@bank.com       / admin123
"""
import os
from app import create_app
from app.extensions import db

app = create_app()

if __name__ == "__main__":
    using_sqlite = "sqlite" in app.config["SQLALCHEMY_DATABASE_URI"]

    with app.app_context():
        db.create_all()
        from sqlalchemy import text
        db.session.execute(text("""
            CREATE OR REPLACE FUNCTION check_customer_loan_before_delete()
            RETURNS TRIGGER AS $$
            BEGIN
                IF EXISTS (
                    SELECT 1
                    FROM customer_account ca
                    JOIN loan_account la ON ca.account_number = la.account_number
                    WHERE ca.customer_ssn = OLD.ssn
                ) THEN
                    RAISE EXCEPTION
                        'Cannot delete customer % (%) because they have an active loan account. Close all loan accounts first.',
                        OLD.name, OLD.ssn;
                END IF;
                RETURN OLD;
            END;
            $$ LANGUAGE plpgsql;
        """))
        db.session.execute(text("""
            DROP TRIGGER IF EXISTS prevent_customer_delete_with_loan ON customer;
        """))
        db.session.execute(text("""
            CREATE TRIGGER prevent_customer_delete_with_loan
            BEFORE DELETE ON customer
            FOR EACH ROW
            EXECUTE FUNCTION check_customer_loan_before_delete();
        """))
        db.session.commit()
    print("\n🏦  CS631 Banking System")
    print(f"    DB  : {app.config['SQLALCHEMY_DATABASE_URI']}")
    print("    URL : http://localhost:5000\n")
    app.run(host="0.0.0.0", port=5000, debug=True)
