from datetime import date
from flask import render_template, redirect, url_for, flash, request
from flask_login import current_user, login_required
from app.events import events_bp
from app.extensions import db
from app.models import Event, Registration
from app.forms import EmptyForm


@events_bp.route('/events')
def index():
    """Browse, search, and filter campus events."""
    query_str = request.args.get('q', '').strip()
    category = request.args.get('category', '').strip()
    time_filter = request.args.get('filter', 'upcoming').strip()

    events_query = Event.query

    # Search filter
    if query_str:
        events_query = events_query.filter(
            (Event.title.ilike(f'%{query_str}%')) |
            (Event.description.ilike(f'%{query_str}%')) |
            (Event.venue.ilike(f'%{query_str}%'))
        )

    # Category filter
    if category and category in Event.CATEGORIES:
        events_query = events_query.filter_by(category=category)

    # Time filter
    today = date.today()
    if time_filter == 'upcoming':
        events_query = events_query.filter(Event.event_date >= today).order_by(
            Event.event_date.asc(), Event.start_time.asc()
        )
    elif time_filter == 'past':
        events_query = events_query.filter(Event.event_date < today).order_by(
            Event.event_date.desc(), Event.start_time.desc()
        )
    else:  # 'all'
        events_query = events_query.order_by(Event.event_date.desc(), Event.start_time.desc())

    events = events_query.all()

    return render_template(
        'events.html',
        events=events,
        categories=Event.CATEGORIES,
        current_category=category,
        query_str=query_str,
        time_filter=time_filter,
        title="Events — CampusConnect"
    )


@events_bp.route('/events/<int:event_id>')
def detail(event_id):
    """View details of a specific event."""
    event = db.get_or_404(Event, event_id)
    form = EmptyForm()

    user_registration = None
    if current_user.is_authenticated and current_user.is_student:
        user_registration = event.registrations.filter_by(
            user_id=current_user.id,
            status='REGISTERED'
        ).first()

    return render_template(
        'event_detail.html',
        event=event,
        user_registration=user_registration,
        form=form,
        title=f"{event.title} — CampusConnect"
    )


@events_bp.route('/events/<int:event_id>/register', methods=['POST'])
@login_required
def register(event_id):
    """Register the logged-in student for an event."""
    form = EmptyForm()
    if not form.validate_on_submit():
        flash("Invalid request token. Please try again.", "danger")
        return redirect(url_for('events.detail', event_id=event_id))

    event = db.get_or_404(Event, event_id)

    # Business rule validation
    can_reg, message = event.can_register(current_user)
    if not can_reg:
        flash(message, "warning")
        return redirect(url_for('events.detail', event_id=event_id))

    try:
        # Check if user had a previous cancelled registration
        existing_reg = Registration.query.filter_by(
            user_id=current_user.id,
            event_id=event.id
        ).first()

        if existing_reg:
            if existing_reg.is_active:
                flash("You are already registered for this event.", "info")
                return redirect(url_for('events.detail', event_id=event_id))
            else:
                existing_reg.reactivate()
        else:
            new_reg = Registration(
                user_id=current_user.id,
                event_id=event.id,
                status='REGISTERED'
            )
            db.session.add(new_reg)

        db.session.commit()
        flash(f"Success! You have officially registered for '{event.title}'.", "success")
        return redirect(url_for('events.detail', event_id=event_id))

    except Exception as e:
        db.session.rollback()
        flash("An unexpected error occurred while processing your registration. Please try again.", "danger")
        return redirect(url_for('events.detail', event_id=event_id))


@events_bp.route('/events/<int:event_id>/cancel', methods=['POST'])
@login_required
def cancel(event_id):
    """Cancel the logged-in student's active registration."""
    form = EmptyForm()
    if not form.validate_on_submit():
        flash("Invalid request token. Please try again.", "danger")
        return redirect(url_for('events.detail', event_id=event_id))

    event = db.get_or_404(Event, event_id)

    if not current_user.is_student:
        flash("Only students can manage registrations.", "warning")
        return redirect(url_for('events.detail', event_id=event_id))

    registration = Registration.query.filter_by(
        user_id=current_user.id,
        event_id=event.id,
        status='REGISTERED'
    ).first()

    if not registration:
        flash("No active registration found for this event.", "warning")
        return redirect(url_for('events.detail', event_id=event_id))

    if not registration.can_cancel:
        flash("Past event registrations cannot be cancelled.", "warning")
        return redirect(url_for('events.detail', event_id=event_id))

    try:
        registration.cancel()
        db.session.commit()
        flash(f"Your registration for '{event.title}' has been cancelled.", "info")
    except Exception as e:
        db.session.rollback()
        flash("Unable to cancel registration due to a server error. Please try again.", "danger")

    # Redirect back to caller (dashboard or registrations page if referrer matches, else event details)
    next_url = request.referrer
    if next_url:
        if 'registrations' in next_url:
            return redirect(url_for('student.registrations'))
        if 'dashboard' in next_url:
            return redirect(url_for('student.dashboard'))
    return redirect(url_for('events.detail', event_id=event_id))
