"""
MediTrack Application Factory.

Initializes the Flask application with all extensions, blueprints,
and configuration. Uses the application factory pattern to support
testing and multiple configurations.
"""

import os
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_wtf import CSRFProtect
from config import Config

# Initialize extensions outside the factory so they can be imported by other modules
db = SQLAlchemy()
login_manager = LoginManager()
login_manager.login_view = 'auth.login'
login_manager.login_message = 'Please log in to access this page.'
login_manager.login_message_category = 'info'
csrf = CSRFProtect()


def create_app(config_class=Config):
    """
    Application factory function.

    Args:
        config_class: Configuration class to use (defaults to Config).

    Returns:
        Flask: The configured Flask application instance.
    """
    app = Flask(__name__)
    app.config.from_object(config_class)

    # Ensure instance directory exists for SQLite
    os.makedirs(os.path.join(app.root_path, '..', 'instance'), exist_ok=True)

    # Initialize Flask extensions with the app
    db.init_app(app)
    login_manager.init_app(app)
    csrf.init_app(app)

    # Register blueprints
    from app.routes.auth import auth_bp
    from app.routes.main import main_bp

    app.register_blueprint(auth_bp)
    app.register_blueprint(main_bp)

    # Create database tables if they don't exist
    with app.app_context():
        from app.models import models  # noqa: F401 — Ensures models are registered
        db.create_all()

    return app
