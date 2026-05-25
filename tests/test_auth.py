"""Authentication route tests for registration and login flows."""

from app.models.models import User


def test_register_creates_user(client, app):
    """POST /register should create a user and redirect to login."""
    response = client.post(
        "/register",
        data={
            "username": "alice",
            "email": "alice@example.com",
            "password": "password123",
            "confirm_password": "password123",
        },
        follow_redirects=False,
    )

    assert response.status_code == 302
    assert "/login" in response.headers["Location"]

    with app.app_context():
        created = User.query.filter_by(username="alice").first()
        assert created is not None
        assert created.email == "alice@example.com"


def test_register_rejects_invalid_email(client):
    """POST /register should reject malformed email addresses."""
    response = client.post(
        "/register",
        data={
            "username": "bob",
            "email": "not-an-email",
            "password": "password123",
            "confirm_password": "password123",
        },
        follow_redirects=True,
    )

    assert response.status_code == 200
    assert b"Please enter a valid email address." in response.data


def test_login_with_valid_credentials(client, app):
    """POST /login should authenticate an existing user."""
    with app.app_context():
        user = User(username="carol", email="carol@example.com")
        user.set_password("password123")
        from app import db

        db.session.add(user)
        db.session.commit()

    response = client.post(
        "/login",
        data={"username": "carol", "password": "password123"},
        follow_redirects=False,
    )

    assert response.status_code == 302
    assert "/dashboard" in response.headers["Location"]
