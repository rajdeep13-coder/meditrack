"""
Database models for MediTrack.

Defines the SQLAlchemy ORM models for users, medications, and medication
adherence logs. These models form the core data layer of the application
and support the medication tracking and streak calculation features.
"""

from datetime import datetime, date
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin
from app import db, login_manager


@login_manager.user_loader
def load_user(user_id):
    """Flask-Login callback to load a user by their ID."""
    return User.query.get(int(user_id))


class User(UserMixin, db.Model):
    """
    User account model.

    Stores authentication credentials and links to the user's medications
    and adherence logs via one-to-many relationships.
    """
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False, index=True)
    email = db.Column(db.String(120), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(256), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # Relationships
    medications = db.relationship(
        'Medication', backref='user', lazy=True, cascade='all, delete-orphan'
    )
    logs = db.relationship(
        'MedicationLog', backref='user', lazy=True, cascade='all, delete-orphan'
    )

    def set_password(self, password):
        """Hash and store the user's password."""
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        """Verify a plaintext password against the stored hash."""
        return check_password_hash(self.password_hash, password)

    def __repr__(self):
        return f'<User {self.username}>'


class Medication(db.Model):
    """
    Medication model.

    Represents a single medication that a user needs to take, including
    its dosage, frequency, scheduled time, and active/inactive status.
    """
    __tablename__ = 'medications'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    name = db.Column(db.String(100), nullable=False)
    dosage = db.Column(db.String(50), nullable=False)
    frequency = db.Column(db.String(50), nullable=False)  # e.g., 'Once daily', 'Twice daily'
    time = db.Column(db.String(10), nullable=False)  # e.g., '08:00', '14:30'
    active = db.Column(db.Boolean, default=True, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # Relationship to adherence logs
    logs = db.relationship(
        'MedicationLog', backref='medication', lazy=True, cascade='all, delete-orphan'
    )

    def __repr__(self):
        return f'<Medication {self.name} ({self.dosage})>'


class MedicationLog(db.Model):
    """
    Medication adherence log model.

    Records whether a specific medication was taken on a given date.
    Used to calculate daily progress and adherence streaks.
    """
    __tablename__ = 'medication_logs'

    id = db.Column(db.Integer, primary_key=True)
    medication_id = db.Column(db.Integer, db.ForeignKey('medications.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    date = db.Column(db.Date, nullable=False, default=date.today)
    taken = db.Column(db.Boolean, default=False, nullable=False)
    taken_at = db.Column(db.DateTime, nullable=True)

    # Ensure one log entry per medication per day
    __table_args__ = (
        db.UniqueConstraint('medication_id', 'date', name='uq_medication_date'),
    )

    def __repr__(self):
        return f'<MedicationLog med={self.medication_id} date={self.date} taken={self.taken}>'
