import json
from datetime import date, datetime
from collections import Counter
from flask import Blueprint, render_template, redirect, url_for, flash, request, abort
from flask_login import login_required, current_user
from sqlalchemy import desc, func
from app.extensions import db
from app.models import User, Event, Registration, Notification
from app.utils import admin_required, send_notification

admin_bp = Blueprint("admin", __name__)

@admin_bp.route("/dashboard")
@admin_required
def dashboard():
    # Basic counts
    total_students = User.query.filter_by(role="student").count()
    total_organizers = User.query.filter_by(role="organizer").count()
    total_events = Event.query.count()
    approved_events = Event.query.filter_by(approval_status="approved").count()
    pending_events = Event.query.filter_by(approval_status="pending").count()
    total_registrations = Registration.query.filter_by(registration_status="confirmed").count()

    # Category distribution for Chart.js
    category_counts = db.session.query(
        Event.category, func.count(Event.id)
    ).group_by(Event.category).all()
    
    cat_labels = [c[0] for c in category_counts]
    cat_values = [c[1] for c in category_counts]

    # Top events by registrations
    top_events = db.session.query(
        Event.title, func.count(Registration.id)
    ).join(Registration, (Registration.event_id == Event.id) & (Registration.registration_status == "confirmed"))\
     .group_by(Event.id).order_by(desc(func.count(Registration.id))).limit(6).all()

    top_event_labels = [t[0][:20] + ("..." if len(t[0]) > 20 else "") for t in top_events]
    top_event_counts = [t[1] for t in top_events]

    # Monthly event creation counts
    event_dates = db.session.query(Event.created_at).all()

    events_by_month = Counter(
        created_at.strftime("%Y-%m")
        for (created_at,) in event_dates
        if created_at is not None
    )

    month_labels = sorted(events_by_month.keys()) if events_by_month else ["Current"]
    month_counts = (
        [events_by_month[m] for m in month_labels]
        if events_by_month else [total_events]
    )

    # Monthly registrations
    registration_dates = db.session.query(
        Registration.registration_date
    ).all()

    regs_by_month = Counter(
        registration_date.strftime("%Y-%m")
        for (registration_date,) in registration_dates
        if registration_date is not None
    )

    reg_month_labels = (
        sorted(regs_by_month.keys()) if regs_by_month else ["Current"]
    )
    reg_month_counts = (
        [regs_by_month[m] for m in reg_month_labels]
        if regs_by_month else [total_registrations]
    )

    # Recent pending events for quick action
    pending_list = Event.query.filter_by(approval_status="pending").order_by(desc(Event.created_at)).limit(5).all()

    return render_template(
        "admin/dashboard.html",
        total_students=total_students,
        total_organizers=total_organizers,
        total_events=total_events,
        approved_events=approved_events,
        pending_events=pending_events,
        total_registrations=total_registrations,
        pending_list=pending_list,
        cat_labels=json.dumps(cat_labels),
        cat_values=json.dumps(cat_values),
        top_event_labels=json.dumps(top_event_labels),
        top_event_counts=json.dumps(top_event_counts),
        month_labels=json.dumps(month_labels),
        month_counts=json.dumps(month_counts),
        reg_month_labels=json.dumps(reg_month_labels),
        reg_month_counts=json.dumps(reg_month_counts)
    )


@admin_bp.route("/events")
@admin_required
def manage_events():
    status_filter = request.args.get("status", "all")
    category_filter = request.args.get("category", "all")
    search = request.args.get("q", "").strip()

    query = Event.query

    if status_filter != "all":
        query = query.filter_by(approval_status=status_filter)
    if category_filter != "all":
        query = query.filter_by(category=category_filter)
    if search:
        query = query.filter(Event.title.ilike(f"%{search}%"))

    events = query.order_by(desc(Event.created_at)).all()

    return render_template(
        "admin/events.html",
        events=events,
        status_filter=status_filter,
        category_filter=category_filter,
        search=search
    )


@admin_bp.route("/events/<int:event_id>/approve", methods=["POST"])
@admin_required
def approve_event(event_id):
    event = db.session.get(Event, event_id)
    if not event:
        abort(404)

    event.approval_status = "approved"

    # Send notification to organizer
    send_notification(
        event.organizer_id,
        "Event Approved!",
        f"Congratulations! Your event '{event.title}' scheduled for {event.event_date.strftime('%B %d, %Y')} has been approved by college administration and is now live."
    )

    db.session.commit()
    flash(f"Event '{event.title}' has been approved and published.", "success")
    return redirect(request.referrer or url_for("admin.manage_events"))


@admin_bp.route("/events/<int:event_id>/reject", methods=["POST"])
@admin_required
def reject_event(event_id):
    event = db.session.get(Event, event_id)
    if not event:
        abort(404)

    reason = request.form.get("reason", "Event does not meet campus activity guidelines.").strip()
    event.approval_status = "rejected"

    # Send notification to organizer
    send_notification(
        event.organizer_id,
        "Event Rejected",
        f"Notice: Your event '{event.title}' was rejected by administration. Reason: {reason}"
    )

    db.session.commit()
    flash(f"Event '{event.title}' has been rejected.", "warning")
    return redirect(request.referrer or url_for("admin.manage_events"))


@admin_bp.route("/events/<int:event_id>/delete", methods=["POST"])
@admin_required
def delete_event(event_id):
    event = db.session.get(Event, event_id)
    if not event:
        abort(404)

    event_title = event.title
    # Notify organizer
    send_notification(
        event.organizer_id,
        "Event Removed by Admin",
        f"Your event '{event_title}' has been removed by the administrator."
    )

    db.session.delete(event)
    db.session.commit()
    flash(f"Event '{event_title}' deleted successfully.", "info")
    return redirect(request.referrer or url_for("admin.manage_events"))


@admin_bp.route("/users")
@admin_required
def manage_users():
    role_filter = request.args.get("role", "all")
    search = request.args.get("q", "").strip()

    query = User.query

    if role_filter != "all":
        query = query.filter_by(role=role_filter)
    if search:
        query = query.filter((User.name.ilike(f"%{search}%")) | (User.email.ilike(f"%{search}%")))

    users = query.order_by(desc(User.created_at)).all()

    return render_template(
        "admin/users.html",
        users=users,
        role_filter=role_filter,
        search=search
    )


@admin_bp.route("/users/<int:user_id>/toggle-role", methods=["POST"])
@admin_required
def toggle_user_role(user_id):
    if user_id == current_user.id:
        flash("You cannot alter your own admin role.", "danger")
        return redirect(url_for("admin.manage_users"))

    user = db.session.get(User, user_id)
    if not user:
        abort(404)

    new_role = request.form.get("new_role")
    if new_role in ["student", "organizer", "admin"]:
        old_role = user.role
        user.role = new_role
        send_notification(
            user.id,
            "Role Updated",
            f"Your account role on CampusConnect has been changed from {old_role.capitalize()} to {new_role.capitalize()}."
        )
        db.session.commit()
        flash(f"User {user.name}'s role updated to {new_role.capitalize()}.", "success")

    return redirect(url_for("admin.manage_users"))


@admin_bp.route("/users/<int:user_id>/delete", methods=["POST"])
@admin_required
def delete_user(user_id):
    if user_id == current_user.id:
        flash("You cannot delete your own admin account.", "danger")
        return redirect(url_for("admin.manage_users"))

    user = db.session.get(User, user_id)
    if not user:
        abort(404)

    user_name = user.name
    db.session.delete(user)
    db.session.commit()
    flash(f"User '{user_name}' has been deleted.", "info")
    return redirect(url_for("admin.manage_users"))


@admin_bp.route("/registrations")
@admin_required
def manage_registrations():
    event_id = request.args.get("event_id", type=int)
    search = request.args.get("q", "").strip()

    query = Registration.query

    if event_id:
        query = query.filter_by(event_id=event_id)
    if search:
        query = query.join(User, Registration.student_id == User.id)\
                     .filter((User.name.ilike(f"%{search}%")) | (User.email.ilike(f"%{search}%")))

    registrations = query.order_by(desc(Registration.registration_date)).limit(100).all()
    events = Event.query.order_by(Event.title.asc()).all()

    return render_template(
        "admin/registrations.html",
        registrations=registrations,
        events=events,
        selected_event_id=event_id,
        search=search
    )
