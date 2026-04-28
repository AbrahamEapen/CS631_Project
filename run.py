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

        # Auto-seed only for local SQLite on first run
        if using_sqlite:
            db_path = os.path.join(os.path.dirname(__file__), "banking.db")
            from app.models.updated_models import User
            if not User.query.first():
                print("Empty database detected — seeding sample data…")
                from seed import run_seed
                run_seed()

    print("\n🏦  CS631 Banking System")
    print(f"    DB  : {app.config['SQLALCHEMY_DATABASE_URI']}")
    print("    URL : http://localhost:5000\n")
    app.run(host="0.0.0.0", port=5000, debug=True)
