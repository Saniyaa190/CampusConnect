from datetime import datetime, date, time
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin
from app.extensions import db, login_manager

class User(UserMixin, db.Model):
    __tablename__ = "users"
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), nullable=False)
    email = db.Column(db.String(150), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(255), nullable=False)
    role = db.Column(db.String(20), nullable=False, default="student", index=True)  # student, organizer, admin
    department = db.Column(db.String(100), nullable=True)
    year = db.Column(db.String(30), nullable=True)  # e.g., "1st Year", "2nd Year", "3rd Year", "4th Year", "Faculty"
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    
    # Relationships
    organized_events = db.relationship("Event", back_populates="organizer", cascade="all, delete-orphan", lazy="dynamic")
    registrations = db.relationship("Registration", back_populates="student", cascade="all, delete-orphan", lazy="dynamic")
    notifications = db.relationship("Notification", back_populates="user", cascade="all, delete-orphan", lazy="dynamic", order_by="desc(Notification.created_at)")

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    @property
    def is_admin(self):
        return self.role == "admin"

    @property
    def is_organizer(self):
        return self.role == "organizer"

    @property
    def is_student(self):
        return self.role == "student"

    @property
    def unread_notifications_count(self):
        return self.notifications.filter_by(is_read=False).count()

    def __repr__(self):
        return f"<User {self.email} ({self.role})>"


@login_manager.user_loader
def load_user(user_id):
    return db.session.get(User, int(user_id))


class Event(db.Model):
    __tablename__ = "events"

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False, index=True)
    description = db.Column(db.Text, nullable=False)
    category = db.Column(db.String(50), nullable=False, index=True)  # Technical, Cultural, Sports, Workshops, Seminars, Competitions, Other
    event_date = db.Column(db.Date, nullable=False, index=True)
    start_time = db.Column(db.Time, nullable=False)
    end_time = db.Column(db.Time, nullable=False)
    venue = db.Column(db.String(150), nullable=False)
    capacity = db.Column(db.Integer, nullable=False, default=100)
    registration_deadline = db.Column(db.Date, nullable=False)
    eligibility = db.Column(db.String(150), default="All Students")
    contact_email = db.Column(db.String(150), nullable=False)
    image = db.Column(db.String(255), default="default_event.jpg")
    organizer_id = db.Column(db.Integer, db.ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    approval_status = db.Column(db.String(20), default="pending", nullable=False, index=True)  # pending, approved, rejected
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)

    # Relationships
    organizer = db.relationship("User", back_populates="organized_events")
    registrations = db.relationship("Registration", back_populates="event", cascade="all, delete-orphan", lazy="dynamic")
    attendances = db.relationship("EventAttendance", back_populates="event", cascade="all, delete-orphan", lazy="dynamic")

    @property
    def registered_count(self):
        return self.registrations.filter_by(registration_status="confirmed").count()

    @property
    def available_seats(self):
        remaining = self.capacity - self.registered_count
        return max(0, remaining)

    @property
    def is_full(self):
        return self.available_seats <= 0

    @property
    def is_past(self):
        today = date.today()
        now_time = datetime.now().time()
        if self.event_date < today:
            return True
        if self.event_date == today and self.end_time < now_time:
            return True
        return False

    @property
    def is_deadline_passed(self):
        return date.today() > self.registration_deadline

    @property
    def is_approved(self):
        return self.approval_status == "approved"

    def can_register(self, user=None):
        if not self.is_approved:
            return False, "This event has not been approved yet."
        if self.is_past:
            return False, "This event has already concluded."
        if self.is_deadline_passed:
            return False, "Registration deadline for this event has passed."
        if self.is_full:
            return False, "This event has reached full capacity."
        if user and user.is_authenticated:
            if not user.is_student:
                return False, "Only students can register for events."
            existing = self.registrations.filter_by(student_id=user.id, registration_status="confirmed").first()
            if existing:
                return False, "You are already registered for this event."
        return True, "Registration is open."

    def __repr__(self):
        return f"<Event {self.title} ({self.approval_status})>"


class Registration(db.Model):
    __tablename__ = "registrations"

    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.Integer, db.ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    event_id = db.Column(db.Integer, db.ForeignKey("events.id", ondelete="CASCADE"), nullable=False, index=True)
    registration_date = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    registration_status = db.Column(db.String(20), default="confirmed", nullable=False)  # confirmed, cancelled
    attendance_status = db.Column(db.String(20), default="not_attended", nullable=False)  # not_attended, attended

    __table_args__ = (
        db.UniqueConstraint("student_id", "event_id", name="uq_student_event"),
    )

    # Relationships
    student = db.relationship("User", back_populates="registrations")
    event = db.relationship("Event", back_populates="registrations")

    def __repr__(self):
        return f"<Registration Student:{self.student_id} Event:{self.event_id} Status:{self.registration_status}>"


class Notification(db.Model):
    __tablename__ = "notifications"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    title = db.Column(db.String(150), nullable=False)
    message = db.Column(db.Text, nullable=False)
    is_read = db.Column(db.Boolean, default=False, nullable=False, index=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)

    # Relationships
    user = db.relationship("User", back_populates="notifications")

    def __repr__(self):
        return f"<Notification User:{self.user_id} Title:{self.title} Read:{self.is_read}>"


class EventAttendance(db.Model):
    __tablename__ = "event_attendances"

    id = db.Column(db.Integer, primary_key=True)
    event_id = db.Column(db.Integer, db.ForeignKey("events.id", ondelete="CASCADE"), nullable=False, index=True)
    student_id = db.Column(db.Integer, db.ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    marked_by = db.Column(db.Integer, db.ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    marked_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)

    event = db.relationship("Event", back_populates="attendances")
    student = db.relationship("User", foreign_keys=[student_id])
    marker = db.relationship("User", foreign_keys=[marked_by])

    def __repr__(self):
        return f"<EventAttendance Event:{self.event_id} Student:{self.student_id}>"
