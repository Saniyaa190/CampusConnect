import csv
import io
from datetime import date, datetime
from flask import Blueprint, render_template, redirect, url_for, flash, request, abort, Response, current_app
from flask_login import login_required, current_user
from sqlalchemy import desc, func
from app.extensions import db
from app.models import Event, Registration, User, EventAttendance
from app.forms import EventForm
from app.utils import organizer_required, save_cover_image, send_notification

organizer_bp = Blueprint("organizer", __name__)

@organizer_bp.route("/dashboard")
@organizer_required
def dashboard():
    today = date.today()

    # Organizer events
    my_events = Event.query.filter_by(organizer_id=current_user.id).all()
    total_events = len(my_events)
    pending_approvals = sum(1 for e in my_events if e.approval_status == "pending")
    approved_events = sum(1 for e in my_events if e.approval_status == "approved")
    
    event_ids = [e.id for e in my_events]

    # Total registrations across organizer events
    if event_ids:
        total_registrations = Registration.query.filter(
            Registration.event_id.in_(event_ids),
            Registration.registration_status == "confirmed"
        ).count()

        recent_registrations = Registration.query.filter(
            Registration.event_id.in_(event_ids),
            Registration.registration_status == "confirmed"
        ).order_by(desc(Registration.registration_date)).limit(6).all()
    else:
        total_registrations = 0
        recent_registrations = []

    upcoming_events = [e for e in my_events if e.event_date >= today and e.approval_status == "approved"]
    upcoming_events.sort(key=lambda x: (x.event_date, x.start_time))

    return render_template(
        "organizer/dashboard.html",
        total_events=total_events,
        pending_approvals=pending_approvals,
        approved_events=approved_events,
        total_registrations=total_registrations,
        upcoming_events=upcoming_events[:4],
        recent_registrations=recent_registrations
    )


@organizer_bp.route("/events")
@organizer_required
def manage_events():
    events = Event.query.filter_by(organizer_id=current_user.id)\
        .order_by(desc(Event.event_date), desc(Event.created_at)).all()
    return render_template("organizer/manage_events.html", events=events)


@organizer_bp.route("/events/create", methods=["GET", "POST"])
@organizer_required
def create_event():
    form = EventForm()
    if request.method == "GET" and not form.contact_email.data:
        form.contact_email.data = current_user.email

    if form.validate_on_submit():
        image_filename = "default_event.jpg"
        if form.image.data and hasattr(form.image.data, "filename") and form.image.data.filename:
            saved_filename = save_cover_image(form.image.data)
            if saved_filename:
                image_filename = saved_filename

        new_event = Event(
            title=form.title.data.strip(),
            category=form.category.data,
            description=form.description.data.strip(),
            event_date=form.event_date.data,
            start_time=form.start_time.data,
            end_time=form.end_time.data,
            venue=form.venue.data.strip(),
            capacity=form.capacity.data,
            registration_deadline=form.registration_deadline.data,
            eligibility=form.eligibility.data.strip(),
            contact_email=form.contact_email.data.strip().lower(),
            image=image_filename,
            organizer_id=current_user.id,
            approval_status="pending"
        )
        db.session.add(new_event)
        db.session.commit()

        # Notify admins about pending approval
        admins = User.query.filter_by(role="admin").all()
        for admin in admins:
            send_notification(
                admin.id,
                "New Event Awaiting Approval",
                f"Organizer '{current_user.name}' submitted a new event '{new_event.title}'. Please review and approve."
            )

        # Notify organizer confirmation
        send_notification(
            current_user.id,
            "Event Submitted",
            f"Your event '{new_event.title}' has been submitted and is currently pending approval by college administration."
        )
        db.session.commit()

        flash(f"Event '{new_event.title}' submitted successfully! It will be listed publicly once approved by an admin.", "success")
        return redirect(url_for("organizer.manage_events"))

    return render_template("organizer/create_event.html", form=form)


@organizer_bp.route("/events/<int:event_id>/edit", methods=["GET", "POST"])
@organizer_required
def edit_event(event_id):
    event = db.session.get(Event, event_id)
    if not event:
        abort(404)
    if event.organizer_id != current_user.id and not current_user.is_admin:
        abort(403)

    form = EventForm(obj=event)
    if form.validate_on_submit():
        if form.image.data and hasattr(form.image.data, "filename") and form.image.data.filename:
            saved_filename = save_cover_image(form.image.data)
            if saved_filename:
                event.image = saved_filename

        event.title = form.title.data.strip()
        event.category = form.category.data
        event.description = form.description.data.strip()
        event.event_date = form.event_date.data
        event.start_time = form.start_time.data
        event.end_time = form.end_time.data
        event.venue = form.venue.data.strip()
        event.capacity = form.capacity.data
        event.registration_deadline = form.registration_deadline.data
        event.eligibility = form.eligibility.data.strip()
        event.contact_email = form.contact_email.data.strip().lower()

        # Notify registered students about updates
        active_regs = event.registrations.filter_by(registration_status="confirmed").all()
        for reg in active_regs:
            send_notification(
                reg.student_id,
                "Event Updated",
                f"The details for '{event.title}' scheduled for {event.event_date.strftime('%B %d, %Y')} have been updated. Please check the event page for details."
            )

        db.session.commit()
        flash(f"Event '{event.title}' updated successfully.", "success")
        return redirect(url_for("organizer.manage_events"))

    return render_template("organizer/edit_event.html", form=form, event=event)


@organizer_bp.route("/events/<int:event_id>/delete", methods=["POST"])
@organizer_required
def delete_event(event_id):
    event = db.session.get(Event, event_id)
    if not event:
        abort(404)
    if event.organizer_id != current_user.id and not current_user.is_admin:
        abort(403)

    event_title = event.title
    active_regs = event.registrations.filter_by(registration_status="confirmed").all()
    for reg in active_regs:
        send_notification(
            reg.student_id,
            "Event Cancelled",
            f"Notice: '{event_title}' has been cancelled and removed by the organizer."
        )

    db.session.delete(event)
    db.session.commit()

    flash(f"Event '{event_title}' has been deleted.", "info")
    return redirect(url_for("organizer.manage_events"))


@organizer_bp.route("/events/<int:event_id>/attendees")
@organizer_required
def event_attendees(event_id):
    event = db.session.get(Event, event_id)
    if not event:
        abort(404)
    if event.organizer_id != current_user.id and not current_user.is_admin:
        abort(403)

    registrations = Registration.query.filter_by(event_id=event.id)\
        .order_by(desc(Registration.registration_date)).all()

    attended_count = sum(1 for r in registrations if r.attendance_status == "attended" and r.registration_status == "confirmed")
    confirmed_count = sum(1 for r in registrations if r.registration_status == "confirmed")

    return render_template(
        "organizer/event_attendees.html",
        event=event,
        registrations=registrations,
        attended_count=attended_count,
        confirmed_count=confirmed_count
    )


@organizer_bp.route("/events/<int:event_id>/attendance/<int:reg_id>/toggle", methods=["POST"])
@organizer_required
def toggle_attendance(event_id, reg_id):
    event = db.session.get(Event, event_id)
    if not event:
        abort(404)
    if event.organizer_id != current_user.id and not current_user.is_admin:
        abort(403)

    registration = db.session.get(Registration, reg_id)
    if not registration or registration.event_id != event.id:
        abort(404)

    if registration.attendance_status == "attended":
        registration.attendance_status = "not_attended"
        # Also clean up EventAttendance if exists
        attendance = EventAttendance.query.filter_by(event_id=event.id, student_id=registration.student_id).first()
        if attendance:
            db.session.delete(attendance)
        flash(f"Marked {registration.student.name} as Not Attended.", "info")
    else:
        registration.attendance_status = "attended"
        attendance = EventAttendance.query.filter_by(event_id=event.id, student_id=registration.student_id).first()
        if not attendance:
            attendance = EventAttendance(
                event_id=event.id,
                student_id=registration.student_id,
                marked_by=current_user.id
            )
            db.session.add(attendance)
        flash(f"Marked {registration.student.name} as Attended!", "success")

    db.session.commit()
    return redirect(url_for("organizer.event_attendees", event_id=event.id))


@organizer_bp.route("/events/<int:event_id>/export-csv")
@organizer_required
def export_csv(event_id):
    event = db.session.get(Event, event_id)
    if not event:
        abort(404)
    if event.organizer_id != current_user.id and not current_user.is_admin:
        abort(403)

    registrations = Registration.query.filter_by(event_id=event.id, registration_status="confirmed")\
        .order_by(Registration.registration_date.asc()).all()

    output = io.StringIO()
    writer = csv.writer(output)
    
    # Header
    writer.writerow(["Registration ID", "Student Name", "Email", "Department", "Academic Year", "Registration Date", "Attendance Status"])
    
    for r in registrations:
        writer.writerow([
            r.id,
            r.student.name,
            r.student.email,
            r.student.department or "N/A",
            r.student.year or "N/A",
            r.registration_date.strftime("%Y-%m-%d %H:%M:%S"),
            r.attendance_status.replace("_", " ").title()
        ])

    csv_data = output.getvalue()
    filename = f"Attendees_{event.title.replace(' ', '_')}_{date.today().strftime('%Y%m%d')}.csv"

    return Response(
        csv_data,
        mimetype="text/csv",
        headers={"Content-Disposition": f"attachment;filename={filename}"}
    )


@organizer_bp.route("/analytics")
@organizer_required
def analytics():
    my_events = Event.query.filter_by(organizer_id=current_user.id).all()
    
    # Event performance metrics
    event_titles = [e.title for e in my_events]
    capacities = [e.capacity for e in my_events]
    reg_counts = [e.registered_count for e in my_events]

    # Category breakdown
    categories_dict = {}
    for e in my_events:
        categories_dict[e.category] = categories_dict.get(e.category, 0) + 1

    return render_template(
        "organizer/analytics.html",
        my_events=my_events,
        event_titles=event_titles,
        capacities=capacities,
        reg_counts=reg_counts,
        category_labels=list(categories_dict.keys()),
        category_values=list(categories_dict.values())
    )
