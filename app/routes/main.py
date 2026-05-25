"""
Main application routes for MediTrack.

Contains the core functionality: landing page, dashboard with daily
medication tracking, medication CRUD operations, and the adherence
streak calculator.
"""

from flask import Blueprint, render_template, redirect, url_for, flash, request, jsonify
from flask_login import login_required, current_user
from datetime import datetime, date, timedelta
from app import db
from app.models.models import Medication, MedicationLog

# Blueprint for main application routes
main_bp = Blueprint('main', __name__)


# ---------------------------------------------------------------------------
#  Landing Page
# ---------------------------------------------------------------------------

@main_bp.route('/')
def index():
    """Render the landing page, or redirect authenticated users to dashboard."""
    if current_user.is_authenticated:
        return redirect(url_for('main.dashboard'))
    return render_template('index.html')


# ---------------------------------------------------------------------------
#  Dashboard
# ---------------------------------------------------------------------------

@main_bp.route('/dashboard')
@login_required
def dashboard():
    """
    Display the user's medication dashboard for today.

    Shows all active medications with checkboxes to mark them as taken,
    the current adherence streak, and a progress bar for today.
    """
    today = date.today()

    # Fetch the user's active medications, sorted by scheduled time
    active_medications = Medication.query.filter_by(
        user_id=current_user.id, active=True
    ).order_by(Medication.time.asc()).all()

    # Build a mapping of medication ID -> today's log (or None)
    today_logs = {}
    for medication in active_medications:
        log_entry = MedicationLog.query.filter_by(
            medication_id=medication.id, date=today
        ).first()
        today_logs[medication.id] = log_entry

    # Calculate the adherence streak
    current_streak = _calculate_streak(current_user.id)

    # Calculate today's progress
    total_medications = len(active_medications)
    taken_count = sum(1 for log in today_logs.values() if log and log.taken)
    progress_percentage = (
        int((taken_count / total_medications) * 100) if total_medications > 0 else 0
    )

    # Determine time-of-day greeting
    current_hour = datetime.now().hour
    if current_hour < 12:
        greeting = 'morning'
    elif current_hour < 17:
        greeting = 'afternoon'
    else:
        greeting = 'evening'

    return render_template(
        'dashboard.html',
        medications=active_medications,
        today_logs=today_logs,
        streak=current_streak,
        today=today,
        total_meds=total_medications,
        taken_count=taken_count,
        progress_percentage=progress_percentage,
        greeting=greeting,
    )


# ---------------------------------------------------------------------------
#  Medication CRUD
# ---------------------------------------------------------------------------

@main_bp.route('/medications')
@login_required
def medications():
    """List all of the current user's medications (active and inactive)."""
    all_medications = Medication.query.filter_by(
        user_id=current_user.id
    ).order_by(Medication.active.desc(), Medication.name.asc()).all()
    return render_template('medications.html', medications=all_medications)


@main_bp.route('/medications/add', methods=['GET', 'POST'])
@login_required
def add_medication():
    """
    Add a new medication.

    GET:  Display the add-medication form.
    POST: Validate and save the new medication, then redirect to dashboard.
    """
    if request.method == 'POST':
        name = request.form.get('name', '').strip()
        dosage = request.form.get('dosage', '').strip()
        frequency = request.form.get('frequency', '').strip()
        scheduled_time = request.form.get('time', '').strip()

        # Validate required fields
        if not all([name, dosage, frequency, scheduled_time]):
            flash('All fields are required.', 'error')
            return render_template('add_medication.html')

        # Create and persist the new medication record
        new_medication = Medication(
            user_id=current_user.id,
            name=name,
            dosage=dosage,
            frequency=frequency,
            time=scheduled_time,
        )
        db.session.add(new_medication)
        db.session.commit()

        flash(f'"{name}" has been added to your medications.', 'success')
        return redirect(url_for('main.dashboard'))

    return render_template('add_medication.html')


@main_bp.route('/medications/<int:med_id>/edit', methods=['GET', 'POST'])
@login_required
def edit_medication(med_id):
    """
    Edit an existing medication.

    GET:  Pre-fill the form with the medication's current values.
    POST: Update the medication record in the database.
    """
    medication = Medication.query.filter_by(
        id=med_id, user_id=current_user.id
    ).first_or_404()

    if request.method == 'POST':
        medication.name = request.form.get('name', '').strip()
        medication.dosage = request.form.get('dosage', '').strip()
        medication.frequency = request.form.get('frequency', '').strip()
        medication.time = request.form.get('time', '').strip()

        if not all([medication.name, medication.dosage, medication.frequency, medication.time]):
            flash('All fields are required.', 'error')
            return render_template('edit_medication.html', medication=medication)

        db.session.commit()
        flash('Medication updated successfully.', 'success')
        return redirect(url_for('main.medications'))

    return render_template('edit_medication.html', medication=medication)


@main_bp.route('/medications/<int:med_id>/delete', methods=['POST'])
@login_required
def delete_medication(med_id):
    """Permanently delete a medication and all its associated logs."""
    medication = Medication.query.filter_by(
        id=med_id, user_id=current_user.id
    ).first_or_404()

    medication_name = medication.name
    db.session.delete(medication)
    db.session.commit()

    flash(f'"{medication_name}" has been removed.', 'info')
    return redirect(url_for('main.medications'))


@main_bp.route('/medications/<int:med_id>/toggle-active', methods=['POST'])
@login_required
def toggle_active(med_id):
    """Toggle a medication's active/inactive status."""
    medication = Medication.query.filter_by(
        id=med_id, user_id=current_user.id
    ).first_or_404()

    medication.active = not medication.active
    db.session.commit()

    status_label = 'activated' if medication.active else 'deactivated'
    flash(f'"{medication.name}" has been {status_label}.', 'info')
    return redirect(url_for('main.medications'))


# ---------------------------------------------------------------------------
#  Toggle "Taken" (AJAX-friendly)
# ---------------------------------------------------------------------------

@main_bp.route('/medications/<int:med_id>/toggle', methods=['POST'])
@login_required
def toggle_taken(med_id):
    """
    Toggle whether a medication was taken today.

    Supports both regular form submissions and AJAX requests.
    For AJAX, returns a JSON payload with updated stats.
    """
    medication = Medication.query.filter_by(
        id=med_id, user_id=current_user.id
    ).first_or_404()

    today = date.today()

    # Find or create today's log entry
    log_entry = MedicationLog.query.filter_by(
        medication_id=med_id, date=today
    ).first()

    if log_entry:
        # Toggle the existing entry
        log_entry.taken = not log_entry.taken
        log_entry.taken_at = datetime.utcnow() if log_entry.taken else None
    else:
        # Create a new entry marked as taken
        log_entry = MedicationLog(
            medication_id=med_id,
            user_id=current_user.id,
            date=today,
            taken=True,
            taken_at=datetime.utcnow(),
        )
        db.session.add(log_entry)

    db.session.commit()

    # If the request came via AJAX, return JSON instead of a redirect
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        updated_streak = _calculate_streak(current_user.id)

        # Recalculate today's progress
        active_meds = Medication.query.filter_by(
            user_id=current_user.id, active=True
        ).all()
        total = len(active_meds)
        taken = MedicationLog.query.filter_by(
            user_id=current_user.id, date=today, taken=True
        ).count()
        progress = int((taken / total) * 100) if total > 0 else 0

        return jsonify({
            'success': True,
            'taken': log_entry.taken,
            'streak': updated_streak,
            'taken_count': taken,
            'total_meds': total,
            'progress_percentage': progress,
        })

    return redirect(url_for('main.dashboard'))


# ---------------------------------------------------------------------------
#  Streak Calculator (private helper)
# ---------------------------------------------------------------------------

def _calculate_streak(user_id):
    """
    Calculate the current consecutive-day adherence streak for a user.

    A "streak day" is a date on which the user took ALL of their currently
    active medications.  The streak counts backwards from today and stops
    at the first day with any missed medication.

    Args:
        user_id: The ID of the user whose streak to calculate.

    Returns:
        int: The number of consecutive days with full adherence.
    """
    active_medications = Medication.query.filter_by(
        user_id=user_id, active=True
    ).all()

    if not active_medications:
        return 0

    active_med_ids = [med.id for med in active_medications]
    total_active_count = len(active_med_ids)
    streak = 0
    check_date = date.today()

    while True:
        # Count how many active medications were taken on this date
        taken_on_date = MedicationLog.query.filter(
            MedicationLog.user_id == user_id,
            MedicationLog.date == check_date,
            MedicationLog.taken.is_(True),
            MedicationLog.medication_id.in_(active_med_ids),
        ).count()

        if taken_on_date >= total_active_count:
            streak += 1
            check_date -= timedelta(days=1)
        else:
            break

    return streak
