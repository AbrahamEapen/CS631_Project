from flask import Flask
from app.extensions import db, jwt
from app.config import Config


def create_app():
    flask_app = Flask(__name__)
    flask_app.config.from_object(Config)

    # ── Extensions ──────────────────────────────────────────────────────
    db.init_app(flask_app)
    jwt.init_app(flask_app)

    # ── Models (avoid circular imports) ─────────────────────────────────
    import app.models  # noqa: F401

    # ── Blueprints ───────────────────────────────────────────────────────
    from app.routes.main         import main_bp
    from app.routes.auth         import auth_bp
    from app.routes.user         import user_bp
    from app.routes.accounts     import accounts_bp
    from app.routes.transactions import transactions_bp
    from app.routes.admin        import admin_bp

    flask_app.register_blueprint(main_bp)
    flask_app.register_blueprint(auth_bp,         url_prefix="/auth")
    flask_app.register_blueprint(user_bp,         url_prefix="/user")
    flask_app.register_blueprint(accounts_bp,     url_prefix="/accounts")
    flask_app.register_blueprint(transactions_bp, url_prefix="/transactions")
    flask_app.register_blueprint(admin_bp,        url_prefix="/admin")

    return flask_app
