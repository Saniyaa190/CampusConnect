from datetime import date, datetime
from flask import Blueprint, render_template, redirect, url_for, flash, request, abort
from flask_login import login_required, current_user
from sqlalchemy import or_, desc, asc
from app.extensions import db
from app.models import Event, Registration, User
from app.utils import send_notification

events_bp = Blueprint("events", __name__)

@events_bp.route("/")
@events_bp.route("/discover")
def discover():
    page = request.args.get("page", 1, type=int)
    search_query = request.args.get("q", "").strip()
    category = request.args.get("category", "").strip()
    venue = request.args.get("venue", "").strip()
    date_filter = request.args.get("date_filter", "upcoming").strip()  # upcoming, all, past
    sort = request.args.get("sort", "upcoming").strip()  # upcoming, newest, popular

    query = Event.query.filter(Event.approval_status == "approved")

    # Search filter
    if search_query:
        query = query.filter(
            or_(
                Event.title.ilike(f"%{search_query}%"),
                Event.description.ilike(f"%{search_query}%"),
                Event.venue.ilike(f"%{search_query}%")
            )
        )

    # Category filter
    if category and category != "All":
        query = query.filter(Event.category == category)

    # Venue filter
    if venue:
        query = query.filter(Event.venue.ilike(f"%{venue}%"))

    # Date filter
    today = date.today()
    if date_filter == "upcoming":
        query = query.filter(Event.event_date >= today)
    elif date_filter == "past":
        query = query.filter(Event.event_date < today)

    # Sorting
    if sort == "newest":
        query = query.order_by(desc(Event.created_at))
    elif sort == "popular":
        # Sort by registrations count
        query = query.order_by(desc(Event.event_date))
    else:  # upcoming default
        if date_filter == "past":
            query = query.order_by(desc(Event.event_date), desc(Event.start_time))
        else:
            query = query.order_by(asc(Event.event_date), asc(Event.start_time))

    events_pagination = query.paginate(page=page, per_page=9, error_out=False)

    # Get distinct venues for filter dropdown
    venues = db.session.query(Event.venue).filter(Event.approval_status == "approved").distinct().all()
    venue_list = sorted([v[0] for v in venues if v[0]])

    return render_template(
        "events/discover.html",
        events_pagination=events_pagination,
        search_query=search_query,
        selected_category=category,
        selected_venue=venue,
        date_filter=date_filter,
        sort=sort,
        venue_list=venue_list
    )


@events_bp.route("/<int:event_id>")
def details(event_id):
    event = db.session.get(Event, event_id)
    if not event:
        abort(404)

    # Only admin, event organizer, or approved events can be viewed by students / public
    if event.approval_status != "approved":
        if not (current_user.is_authenticated and (current_user.is_admin or event.organizer_id == current_user.id)):
            flash("This event is pending administrative approval and is not publicly visible.", "warning")
            return redirect(url_for("events.discover"))

    # Check registration status for logged in student
    user_registration = None
    if current_user.is_authenticated and current_user.is_student:
        user_registration = Registration.query.filter_by(
            student_id=current_user.id,
            event_id=event.id
        ).first()

    can_reg, reg_msg = event.can_register(current_user)

    return render_template(
        "events/details.html",
        event=event,
        user_registration=user_registration,
        can_reg=can_reg,
        reg_msg=reg_msg
    )


@events_bp.route("/<int:event_id>/register", methods=["POST"])
@login_required
def register(event_id):
    if not current_user.is_student:
        flash("Only student accounts can register for events.", "danger")
        return redirect(url_for("events.details", event_id=event_id))

    event = db.session.get(Event, event_id)
    if not event:
        abort(404)

    # Validate registration eligibility
    can_reg, reg_msg = event.can_register(current_user)
    if not can_reg:
        flash(reg_msg, "danger")
        return redirect(url_for("events.details", event_id=event_id))

    # Check existing registration
    existing_reg = Registration.query.filter_by(
        student_id=current_user.id,
        event_id=event.id
    ).first()

    if existing_reg:
        if existing_reg.registration_status == "confirmed":
            flash("You are already registered for this event.", "info")
            return redirect(url_for("events.details", event_id=event.id))
        else:
            # Re-confirm previous cancelled registration
            existing_reg.registration_status = "confirmed"
            existing_reg.registration_date = datetime.utcnow()
    else:
        new_reg = Registration(
            student_id=current_user.id,
            event_id=event.id,
            registration_status="confirmed",
            attendance_status="not_attended"
        )
        db.session.add(new_reg)

    # Send notifications
    # 1. Student notification
    send_notification(
        current_user.id,
        "Registration Confirmed!",
        f"You have successfully registered for '{event.title}'. It takes place on {event.event_date.strftime('%B %d, %Y')} at {event.venue}."
    )
    # 2. Organizer notification
    send_notification(
        event.organizer_id,
        "New Event Registration",
        f"{current_user.name} ({current_user.department}, {current_user.year}) registered for '{event.title}'."
    )

    db.session.commit()
    flash(f"Congratulations! You have successfully registered for {event.title}.", "success")
    return redirect(url_for("events.details", event_id=event.id))


@events_bp.route("/<int:event_id>/cancel", methods=["POST"])
@login_required
def cancel(event_id):
    if not current_user.is_student:
        flash("Only students can manage registrations.", "danger")
        return redirect(url_for("events.details", event_id=event_id))

    event = db.session.get(Event, event_id)
    if not event:
        abort(404)

    registration = Registration.query.filter_by(
        student_id=current_user.id,
        event_id=event.id,
        registration_status="confirmed"
    ).first()

    if not registration:
        flash("No active registration found for this event.", "warning")
        return redirect(url_for("events.details", event_id=event_id))

    if event.is_past:
        flash("Cannot cancel registration for an event that has already occurred.", "danger")
        return redirect(url_for("events.details", event_id=event_id))

    registration.registration_status = "cancelled"

    # Notifications
    send_notification(
        current_user.id,
        "Registration Cancelled",
        f"Your registration for '{event.title}' has been cancelled."
    )
    send_notification(
        event.organizer_id,
        "Registration Cancellation",
        f"{current_user.name} cancelled their registration for '{event.title}'."
    )

    db.session.commit()
    flash(f"Your registration for '{event.title}' has been cancelled.", "info")
    
    # Redirect back to my_registrations if referrer was there
    if "my-registrations" in (request.referrer or ""):
        return redirect(url_for("student.my_registrations"))
    return redirect(url_for("events.details", event_id=event.id))
