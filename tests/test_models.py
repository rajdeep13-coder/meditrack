"""Model-level tests for user password hashing and medication log rules."""

from datetime import date

import pytest
from sqlalchemy.exc import IntegrityError

from app import db
from app.models.models import Medication, MedicationLog, User


def test_user_password_hashing(app):
    """User password checks should pass only for matching password."""
    with app.app_context():
        user = User(username="dave", email="dave@example.com")
        user.set_password("secret-pass")

        assert user.password_hash != "secret-pass"
        assert user.check_password("secret-pass") is True
        assert user.check_password("wrong-pass") is False


def test_medication_log_unique_per_medication_date(app):
    """MedicationLog should enforce one entry per medication per day."""
    with app.app_context():
        user = User(username="emma", email="emma@example.com")
        user.set_password("password123")
        db.session.add(user)
        db.session.flush()

        medication = Medication(
            user_id=user.id,
            name="Aspirin",
            dosage="100mg",
            frequency="Once daily",
            time="08:00",
        )
        db.session.add(medication)
        db.session.flush()

        first_log = MedicationLog(
            medication_id=medication.id,
            user_id=user.id,
            date=date.today(),
            taken=True,
        )
        duplicate_log = MedicationLog(
            medication_id=medication.id,
            user_id=user.id,
            date=date.today(),
            taken=False,
        )

        db.session.add(first_log)
        db.session.commit()

        db.session.add(duplicate_log)
        with pytest.raises(IntegrityError):
            db.session.commit()

        db.session.rollback()
