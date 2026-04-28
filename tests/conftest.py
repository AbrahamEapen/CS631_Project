import pytest
from app.extensions import db
from app import create_app


@pytest.fixture(scope="session")
def app():
    """
    Creates a fully isolated Flask app for testing.
    Uses in-memory SQLite to avoid CI/Postgres dependency issues.
    """

    app = create_app()

    # TEST CONFIGURATION
    app.config.update(
        TESTING=True,
        SQLALCHEMY_DATABASE_URI="sqlite:///:memory:",
        SQLALCHEMY_TRACK_MODIFICATIONS=False,
        JWT_SECRET_KEY="test-secret-key",
        WTF_CSRF_ENABLED=False
    )

    with app.app_context():
        # IMPORTANT:
        # Ensure all models are imported BEFORE create_all()
        import app.models  # noqa: F401

        db.create_all()

        yield app

        # CLEANUP
        db.session.remove()
        db.drop_all()


@pytest.fixture(scope="function")
def client(app):
    """
    Provides a test client with fresh DB state per test.
    """
    return app.test_client()


@pytest.fixture(scope="function")
def runner(app):
    """
    CLI runner (if needed for future extensions).
    """
    return app.test_cli_runner()