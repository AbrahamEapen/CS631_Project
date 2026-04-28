-- CS631 Banking System — PostgreSQL init script
-- Runs automatically when the Postgres container starts for the first time.
-- The Python app (SQLAlchemy) creates all tables via db.create_all(),
-- so this file just ensures the database and extensions are ready.

-- Enable useful extensions
CREATE EXTENSION IF NOT EXISTS "pgcrypto";

-- Signal that init completed
SELECT 'CS631 database initialised' AS status;
