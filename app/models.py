from datetime import datetime, timezone
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin
from app.extensions import db, login_manager


def utc_now():
    """Return current UTC datetime."""
    return datetime.now(timezone.utc)


class User(UserMixin, db.Model):
    """User account model for Students and Administrators."""
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    full_name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(255), nullable=False)
    role = db.Column(db.String(20), nullable=False, default='STUDENT')  # 'STUDENT' or 'ADMIN'
    created_at = db.Column(db.DateTime, default=utc_now, nullable=False)

    # Relationships
    registrations = db.relationship(
        'Registration',
        backref='user',
        lazy='dynamic',
        cascade='all, delete-orphan'
    )
    events_created = db.relationship(
        'Event',
        backref='creator',
        lazy='dynamic'
    )

    def set_password(self, password):
        """Hash and securely store user password using Werkzeug."""
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        """Verify candidate password against stored password hash."""
        return check_password_hash(self.password_hash, password)

    @property
    def is_admin(self):
        """Check if user has the ADMIN role."""
        return self.role == 'ADMIN'

    @property
    def is_student(self):
        """Check if user has the STUDENT role."""
        return self.role == 'STUDENT'

    def is_registered_for(self, event_id):
        """Check if student currently has an active registration for an event."""
        return self.registrations.filter_by(event_id=event_id, status='REGISTERED').first() is not None

    def get_registration_for(self, event_id):
        """Retrieve active registration record for an event if it exists."""
        return self.registrations.filter_by(event_id=event_id, status='REGISTERED').first()

    def __repr__(self):
        return f"<User {self.id}: {self.email} ({self.role})>"


@login_manager.user_loader
def load_user(user_id):
    """Flask-Login user loader callback using modern db.session.get."""
    try:
        return db.session.get(User, int(user_id))
    except (ValueError, TypeError):
        return None


class Event(db.Model):
    """College Event model."""
    __tablename__ = 'events'

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(150), nullable=False, index=True)
    description = db.Column(db.Text, nullable=False)
    category = db.Column(db.String(50), nullable=False, index=True)
    venue = db.Column(db.String(150), nullable=False)
    event_date = db.Column(db.Date, nullable=False, index=True)
    start_time = db.Column(db.Time, nullable=False)
    capacity = db.Column(db.Integer, nullable=False, default=50)
    created_at = db.Column(db.DateTime, default=utc_now, nullable=False)
    created_by = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='SET NULL'), nullable=True)

    # Relationships
    registrations = db.relationship(
        'Registration',
        backref='event',
        lazy='dynamic',
        cascade='all, delete-orphan'
    )

    # Category choices for validation
    CATEGORIES = ['Technology', 'Cultural', 'Sports', 'Workshop', 'Seminar']

    @property
    def active_registrations_count(self):
        """Count registrations with status REGISTERED."""
        return self.registrations.filter_by(status='REGISTERED').count()

    @property
    def available_seats(self):
        """Calculate remaining seats available for registration."""
        remaining = self.capacity - self.active_registrations_count
        return max(0, remaining)

    @property
    def is_full(self):
        """Check if event capacity has been reached."""
        return self.available_seats <= 0

    @property
    def is_past(self):
        """Check if event has already occurred based on current local date and time."""
        now = datetime.now()
        event_datetime = datetime.combine(self.event_date, self.start_time)
        return event_datetime < now

    @property
    def formatted_date(self):
        """Human-readable date format, e.g. 'Oct 28, 2026'."""
        return self.event_date.strftime('%b %d, %Y')

    @property
    def formatted_time(self):
        """Human-readable 12-hour time format, e.g. '10:30 AM'."""
        return self.start_time.strftime('%I:%M %p')

    @property
    def occupancy_percentage(self):
        """Calculate occupancy percentage for progress meters."""
        if not self.capacity or self.capacity <= 0:
            return 0
        pct = (self.active_registrations_count / self.capacity) * 100
        return min(100, round(pct, 1))

    def can_register(self, user):
        """Check if user can register for this event."""
        if not user or not user.is_authenticated:
            return False, "You must be logged in to register."
        if not user.is_student:
            return False, "Only students can register for events."
        if self.is_past:
            return False, "Registration closed: this event has already taken place."
        if user.is_registered_for(self.id):
            return False, "You are already registered for this event."
        if self.is_full:
            return False, "Sorry, this event is fully booked."
        return True, "Eligible to register."

    def __repr__(self):
        return f"<Event {self.id}: {self.title} ({self.category})>"


class Registration(db.Model):
    """Event Registration model linking Students and Events."""
    __tablename__ = 'registrations'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='CASCADE'), nullable=False, index=True)
    event_id = db.Column(db.Integer, db.ForeignKey('events.id', ondelete='CASCADE'), nullable=False, index=True)
    registration_date = db.Column(db.DateTime, default=utc_now, nullable=False)
    status = db.Column(db.String(20), nullable=False, default='REGISTERED', index=True)  # 'REGISTERED' or 'CANCELLED'

    # Database table arguments: index for fast lookup of a user's status for an event
    __table_args__ = (
        db.Index('idx_user_event_status', 'user_id', 'event_id', 'status'),
    )

    @property
    def is_active(self):
        """Check if registration is in active REGISTERED state."""
        return self.status == 'REGISTERED'

    @property
    def is_cancelled(self):
        """Check if registration has been cancelled."""
        return self.status == 'CANCELLED'

    @property
    def can_cancel(self):
        """Student can cancel if registration is active and the event hasn't already passed."""
        return self.is_active and (self.event is None or not self.event.is_past)

    def cancel(self):
        """Cancel registration."""
        self.status = 'CANCELLED'

    def reactivate(self):
        """Reactivate previously cancelled registration."""
        self.status = 'REGISTERED'
        self.registration_date = utc_now()

    def __repr__(self):
        return f"<Registration {self.id}: User {self.user_id} -> Event {self.event_id} [{self.status}]>"
