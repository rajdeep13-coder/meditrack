"""
Configuration module for the MediTrack application.

Defines application-wide settings including database URI, secret key,
and other Flask configuration options. Values can be overridden via
environment variables for production deployments.
"""

import os
import secrets


class Config:
    """Base configuration class for MediTrack."""

    # Secret key for session management and CSRF protection
    # Secret key for session management and CSRF protection.
    # Uses an environment value if provided. In production the environment
    # variable must be set; in development an ephemeral key is generated
    # at runtime (not committed anywhere) to avoid hardcoding secrets.
    SECRET_KEY = os.environ.get('SECRET_KEY')

    if not SECRET_KEY:
        if os.environ.get('FLASK_ENV') == 'production':
            raise RuntimeError('SECRET_KEY must be set as an environment variable in production')
        # Development: generate an ephemeral secret key (not stored on disk)
        SECRET_KEY = secrets.token_urlsafe(32)

    # SQLite database path (default: meditrack.db in the instance folder)
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or \
        'sqlite:///' + os.path.join(os.path.abspath(os.path.dirname(__file__)), 'instance', 'meditrack.db')

    # Disable modification tracking to save resources
    SQLALCHEMY_TRACK_MODIFICATIONS = False
