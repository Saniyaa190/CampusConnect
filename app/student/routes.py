from datetime import date
from flask import Blueprint, render_template, redirect, url_for
from flask_login import login_required, current_user
from sqlalchemy import desc
from app.extensions import db
from app.models import Event, Registration, Notification
from app.utils import student_required

student_bp = Blueprint("student", __name__)

@student_bp.route("/dashboard")
@student_required
def dashboard():
    today = date.today()

    # Registrations query
    registrations = Registration.query.filter_by(
        student_id=current_user.id,
        registration_status="confirmed"
    ).all()

    total_registered = len(registrations)

    # Split into upcoming and past
    upcoming_registered_events = []
    completed_events_count = 0

    for reg in registrations:
        ev = reg.event
        if ev.event_date >= today:
            upcoming_registered_events.append(ev)
        else:
            completed_events_count += 1

    # Available events to explore (approved, future, not yet registered)
    registered_event_ids = [reg.event_id for reg in registrations]
    available_events_query = Event.query.filter(
        Event.approval_status == "approved",
        Event.event_date >= today
    )
    if registered_event_ids:
        available_events_query = available_events_query.filter(~Event.id.in_(registered_event_ids))
    
    available_events = available_events_query.order_by(Event.event_date.asc()).limit(4).all()
    total_available_count = available_events_query.count()

    # Recent notifications
    recent_notifications = Notification.query.filter_by(user_id=current_user.id)\
        .order_by(desc(Notification.created_at)).limit(5).all()

    return render_template(
        "student/dashboard.html",
        total_registered=total_registered,
        upcoming_count=len(upcoming_registered_events),
        completed_count=completed_events_count,
        total_available_count=total_available_count,
        upcoming_events=upcoming_registered_events[:4],
        available_events=available_events,
        recent_notifications=recent_notifications
    )


@student_bp.route("/my-registrations")
@student_required
def my_registrations():
    registrations = Registration.query.filter_by(student_id=current_user.id)\
        .order_by(desc(Registration.registration_date)).all()
    
    today = date.today()

    return render_template(
        "student/my_registrations.html",
        registrations=registrations,
        today=today
    )
