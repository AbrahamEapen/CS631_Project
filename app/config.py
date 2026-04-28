import os

class Config:
    # Use DATABASE_URL env var when set (Docker/Postgres),
    # fall back to a local SQLite file for plain `python run.py`.
    SQLALCHEMY_DATABASE_URI = os.getenv(
        "DATABASE_URL",
        "sqlite:///banking.db"
    )
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    JWT_SECRET_KEY = os.getenv("JWT_SECRET", "cs631-secret-key")
    SECRET_KEY     = os.getenv("SECRET_KEY",  "cs631-flask-secret")
