"""Medication route tests covering CRUD and intake logging behavior."""

from app import db
from app.models.models import Medication, User


def _create_and_login_user(client, app, username="zoe", email="zoe@example.com"):
    """Helper to create a user directly and authenticate through /login."""
    with app.app_context():
        user = User(username=username, email=email)
        user.set_password("password123")
        db.session.add(user)
        db.session.commit()

    login_response = client.post(
        "/login",
        data={"username": username, "password": "password123"},
        follow_redirects=False,
    )
    assert login_response.status_code == 302


def test_dashboard_requires_authentication(client):
    """GET /dashboard should redirect anonymous users to login."""
    response = client.get("/dashboard", follow_redirects=False)
    assert response.status_code == 302
    assert "/login" in response.headers["Location"]


def test_add_medication_creates_record(client, app):
    """POST /medications/add should persist medication for logged-in user."""
    _create_and_login_user(client, app)

    response = client.post(
        "/medications/add",
        data={
            "name": "Metformin",
            "dosage": "500mg",
            "frequency": "Once daily",
            "time": "09:00",
        },
        follow_redirects=False,
    )

    assert response.status_code == 302
    assert "/dashboard" in response.headers["Location"]

    with app.app_context():
        medication = Medication.query.filter_by(name="Metformin").first()
        assert medication is not None
        assert medication.dosage == "500mg"


def test_toggle_medication_taken_ajax_returns_json(client, app):
    """POST /medications/<id>/toggle should return JSON for AJAX requests."""
    _create_and_login_user(client, app, username="mia", email="mia@example.com")

    with app.app_context():
        user = User.query.filter_by(username="mia").first()
        medication = Medication(
            user_id=user.id,
            name="Vitamin D",
            dosage="1 tablet",
            frequency="Once daily",
            time="10:00",
        )
        db.session.add(medication)
        db.session.commit()
        med_id = medication.id

    response = client.post(
        f"/medications/{med_id}/toggle",
        headers={"X-Requested-With": "XMLHttpRequest"},
    )

    assert response.status_code == 200
    payload = response.get_json()
    assert payload is not None
    assert payload["success"] is True
    assert "progress_percentage" in payload
