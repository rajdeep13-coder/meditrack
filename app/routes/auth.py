"""
Authentication routes for MediTrack.

Handles user registration, login, and logout functionality.
Uses Flask-Login for session management and Werkzeug for
secure password hashing.
"""

from flask import Blueprint, render_template, redirect, url_for, flash, request
import re
from flask_login import login_user, logout_user, login_required, current_user
from app import db
from app.models.models import User

# Blueprint for authentication-related routes
auth_bp = Blueprint('auth', __name__)


@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    """
    Handle new user registration.

    GET: Display the registration form.
    POST: Validate input, create a new user account, and redirect to login.
    """
    # Redirect already-authenticated users to the dashboard
    if current_user.is_authenticated:
        return redirect(url_for('main.dashboard'))

    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        email = request.form.get('email', '').strip().lower()
        password = request.form.get('password', '')
        confirm_password = request.form.get('confirm_password', '')

        # --- Input Validation ---
        if not all([username, email, password, confirm_password]):
            flash('All fields are required.', 'error')
            return render_template('register.html')

        if len(username) < 3:
            flash('Username must be at least 3 characters long.', 'error')
            return render_template('register.html')

        if password != confirm_password:
            flash('Passwords do not match.', 'error')
            return render_template('register.html')

        if len(password) < 6:
            flash('Password must be at least 6 characters long.', 'error')
            return render_template('register.html')

        # Basic email format validation
        email_regex = r'^[^@\s]+@[^@\s]+\.[^@\s]+$'
        if not re.match(email_regex, email):
            flash('Please enter a valid email address.', 'error')
            return render_template('register.html')

        # Check for existing username
        if User.query.filter_by(username=username).first():
            flash('That username is already taken.', 'error')
            return render_template('register.html')

        # Check for existing email
        if User.query.filter_by(email=email).first():
            flash('That email is already registered.', 'error')
            return render_template('register.html')

        # --- Create New User ---
        new_user = User(username=username, email=email)
        new_user.set_password(password)
        db.session.add(new_user)
        db.session.commit()

        flash('Account created successfully! Please log in.', 'success')
        return redirect(url_for('auth.login'))

    return render_template('register.html')


@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    """
    Handle user login.

    GET: Display the login form.
    POST: Authenticate the user and create a session.
    """
    if current_user.is_authenticated:
        return redirect(url_for('main.dashboard'))

    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        password = request.form.get('password', '')

        # Attempt to find the user and verify the password
        user = User.query.filter_by(username=username).first()

        if user and user.check_password(password):
            login_user(user, remember=True)
            flash(f'Welcome back, {user.username}!', 'success')

            # Redirect to the page the user originally requested, if any
            next_page = request.args.get('next')
            return redirect(next_page or url_for('main.dashboard'))

        flash('Invalid username or password.', 'error')

    return render_template('login.html')


@auth_bp.route('/logout')
@login_required
def logout():
    """Log the current user out and redirect to the login page."""
    logout_user()
    flash('You have been logged out successfully.', 'info')
    return redirect(url_for('auth.login'))
