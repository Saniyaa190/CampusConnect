from datetime import date
from flask import render_template
from app.main import main_bp
from app.models import Event, User, Registration


@main_bp.route('/')
def home():
    """CampusConnect Landing Page."""
    today = date.today()
    # Fetch upcoming featured events
    featured_events = (
        Event.query
        .filter(Event.event_date >= today)
        .order_by(Event.event_date.asc(), Event.start_time.asc())
        .limit(6)
        .all()
    )

    # Calculate headline community stats
    total_events = Event.query.count()
    total_students = User.query.filter_by(role='STUDENT').count()
    total_registrations = Registration.query.filter_by(status='REGISTERED').count()

    return render_template(
        'home.html',
        featured_events=featured_events,
        total_events=total_events,
        total_students=total_students,
        total_registrations=total_registrations,
        categories=Event.CATEGORIES,
        title="CampusConnect — Your Campus. Your Community."
    )


@main_bp.route('/about')
def about():
    """About CampusConnect Platform."""
    return render_template('about.html', title="About — CampusConnect")
