from functools import wraps
from datetime import date
from flask import render_template, redirect, url_for, flash, abort
from flask_login import login_required, current_user
from app.student import student_bp
from app.models import Registration, Event
from app.forms import EmptyForm


def student_required(f):
    """Ensure authenticated user is a student."""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated:
            return redirect(url_for('auth.login'))
        if not current_user.is_student:
            flash("Access denied: This section is for students only.", "danger")
            return redirect(url_for('admin.dashboard'))
        return f(*args, **kwargs)
    return decorated_function


@student_bp.route('/dashboard')
@login_required
@student_required
def dashboard():
    """Student overview dashboard."""
    today = date.today()

    # Query all registrations for this student joined with event
    all_registrations = (
        Registration.query
        .filter_by(user_id=current_user.id)
        .join(Event)
        .order_by(Event.event_date.asc())
        .all()
    )

    active_regs = [r for r in all_registrations if r.is_active]
    upcoming_regs = [r for r in active_regs if r.event.event_date >= today]
    past_regs = [r for r in active_regs if r.event.event_date < today]
    cancelled_regs = [r for r in all_registrations if r.is_cancelled]

    form = EmptyForm()

    return render_template(
        'student_dashboard.html',
        upcoming_registrations=upcoming_regs,
        total_registered=len(active_regs),
        total_upcoming=len(upcoming_regs),
        total_past=len(past_regs),
        total_cancelled=len(cancelled_regs),
        form=form,
        title="Student Dashboard — CampusConnect"
    )


@student_bp.route('/registrations')
@login_required
@student_required
def registrations():
    """Detailed personal registrations table with cancellation options."""
    registrations_list = (
        Registration.query
        .filter_by(user_id=current_user.id)
        .join(Event)
        .order_by(Event.event_date.desc(), Registration.registration_date.desc())
        .all()
    )

    form = EmptyForm()

    return render_template(
        'my_registrations.html',
        registrations=registrations_list,
        form=form,
        title="My Registrations — CampusConnect"
    )
