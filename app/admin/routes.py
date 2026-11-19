from functools import wraps
from datetime import date
from flask import render_template, redirect, url_for, flash, request, abort
from flask_login import login_required, current_user
from app.admin import admin_bp
from app.extensions import db
from app.models import Event, User, Registration
from app.forms import EventForm, EmptyForm


def admin_required(f):
    """Ensure authenticated user is an Administrator."""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated:
            return redirect(url_for('auth.login', next=request.url))
        if not current_user.is_admin:
            abort(403)
        return f(*args, **kwargs)
    return decorated_function


@admin_bp.route('/dashboard')
@login_required
@admin_required
def dashboard():
    """Admin analytics and event management hub."""
    today = date.today()
    all_events = Event.query.order_by(Event.event_date.desc(), Event.start_time.desc()).all()

    total_events = len(all_events)
    total_students = User.query.filter_by(role='STUDENT').count()
    total_registrations = Registration.query.filter_by(status='REGISTERED').count()
    upcoming_events = len([e for e in all_events if e.event_date >= today])

    # Calculate overall capacity and occupancy
    total_capacity = sum(e.capacity for e in all_events)
    active_booked = sum(e.active_registrations_count for e in all_events)
    overall_occupancy = round((active_booked / total_capacity * 100), 1) if total_capacity > 0 else 0

    # Category distribution stats
    category_counts = {}
    for cat in Event.CATEGORIES:
        category_counts[cat] = sum(1 for e in all_events if e.category == cat)

    delete_form = EmptyForm()

    return render_template(
        'admin_dashboard.html',
        events=all_events,
        total_events=total_events,
        total_students=total_students,
        total_registrations=total_registrations,
        upcoming_events=upcoming_events,
        overall_occupancy=overall_occupancy,
        category_counts=category_counts,
        delete_form=delete_form,
        title="Admin Dashboard — CampusConnect"
    )


@admin_bp.route('/events/create', methods=['GET', 'POST'])
@login_required
@admin_required
def create_event():
    """Create a new college event."""
    form = EventForm()
    if form.validate_on_submit():
        event = Event(
            title=form.title.data.strip(),
            category=form.category.data,
            description=form.description.data.strip(),
            venue=form.venue.data.strip(),
            event_date=form.event_date.data,
            start_time=form.start_time.data,
            capacity=form.capacity.data,
            created_by=current_user.id
        )
        db.session.add(event)
        db.session.commit()

        flash(f"Event '{event.title}' has been successfully scheduled!", "success")
        return redirect(url_for('admin.dashboard'))

    return render_template(
        'create_event.html',
        form=form,
        title="Create Event — CampusConnect"
    )


@admin_bp.route('/events/<int:event_id>/edit', methods=['GET', 'POST'])
@login_required
@admin_required
def edit_event(event_id):
    """Edit existing event details."""
    event = db.get_or_404(Event, event_id)
    form = EventForm(obj=event)

    if form.validate_on_submit():
        # Prevent setting capacity below currently active registered count
        if form.capacity.data < event.active_registrations_count:
            flash(
                f"Cannot reduce capacity to {form.capacity.data}. "
                f"There are currently {event.active_registrations_count} active registered students.",
                "danger"
            )
            return render_template('edit_event.html', form=form, event=event, title=f"Edit {event.title}")

        event.title = form.title.data.strip()
        event.category = form.category.data
        event.description = form.description.data.strip()
        event.venue = form.venue.data.strip()
        event.event_date = form.event_date.data
        event.start_time = form.start_time.data
        event.capacity = form.capacity.data

        db.session.commit()
        flash(f"Event '{event.title}' updated successfully.", "success")
        return redirect(url_for('admin.dashboard'))

    return render_template(
        'edit_event.html',
        form=form,
        event=event,
        title=f"Edit {event.title} — CampusConnect"
    )


@admin_bp.route('/events/<int:event_id>/delete', methods=['POST'])
@login_required
@admin_required
def delete_event(event_id):
    """Delete an event and cascade-remove its registrations."""
    form = EmptyForm()
    if not form.validate_on_submit():
        flash("Invalid request token.", "danger")
        return redirect(url_for('admin.dashboard'))

    event = db.get_or_404(Event, event_id)
    event_title = event.title

    db.session.delete(event)
    db.session.commit()

    flash(f"Event '{event_title}' and its registrations were removed.", "info")
    return redirect(url_for('admin.dashboard'))


@admin_bp.route('/events/<int:event_id>/registrations')
@login_required
@admin_required
def event_participants(event_id):
    """View detailed list of student participants for an event."""
    event = db.get_or_404(Event, event_id)
    registrations = (
        Registration.query
        .filter_by(event_id=event.id)
        .join(User)
        .order_by(Registration.registration_date.desc())
        .all()
    )

    return render_template(
        'event_participants.html',
        event=event,
        registrations=registrations,
        title=f"Participants — {event.title}"
    )
