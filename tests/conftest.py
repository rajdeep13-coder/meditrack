"""Pytest fixtures for MediTrack test suite."""

import os
import tempfile

import pytest

from app import create_app, db


class TestConfig:
    """Test configuration with an isolated SQLite database."""

    TESTING = True
    WTF_CSRF_ENABLED = False
    SECRET_KEY = "test-secret-key"
    SQLALCHEMY_DATABASE_URI = "sqlite:///"
    SQLALCHEMY_TRACK_MODIFICATIONS = False


@pytest.fixture()
def app():
    """Create a Flask app instance backed by a temporary SQLite file."""
    fd, db_path = tempfile.mkstemp(prefix="meditrack-test-", suffix=".db")
    os.close(fd)

    class FileDBConfig(TestConfig):
        SQLALCHEMY_DATABASE_URI = f"sqlite:///{db_path}"

    flask_app = create_app(FileDBConfig)

    with flask_app.app_context():
        db.create_all()

    yield flask_app

    with flask_app.app_context():
        db.session.remove()
        db.drop_all()
        db.engine.dispose()

    if os.path.exists(db_path):
        os.unlink(db_path)


@pytest.fixture()
def client(app):
    """Create a test client for request-based tests."""
    return app.test_client()
