from datetime import date
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, BooleanField, TextAreaField, SelectField, IntegerField, DateField, TimeField
from wtforms.validators import DataRequired, Email, Length, EqualTo, ValidationError, NumberRange
from app.models import User, Event


class SignupForm(FlaskForm):
    """Student registration form."""
    full_name = StringField(
        'Full Name',
        validators=[
            DataRequired(message="Full name is required."),
            Length(min=2, max=100, message="Full name must be between 2 and 100 characters.")
        ],
        render_kw={"placeholder": "e.g., Jane Doe"}
    )
    email = StringField(
        'College Email Address',
        validators=[
            DataRequired(message="Email address is required."),
            Email(message="Please enter a valid email address."),
            Length(max=120)
        ],
        render_kw={"placeholder": "student@college.edu"}
    )
    password = PasswordField(
        'Password',
        validators=[
            DataRequired(message="Password is required."),
            Length(min=6, max=100, message="Password must be at least 6 characters long.")
        ],
        render_kw={"placeholder": "••••••••"}
    )
    confirm_password = PasswordField(
        'Confirm Password',
        validators=[
            DataRequired(message="Please confirm your password."),
            EqualTo('password', message="Passwords must match.")
        ],
        render_kw={"placeholder": "••••••••"}
    )
    submit = SubmitField('Create Account')

    def validate_email(self, field):
        """Ensure email is unique across all users."""
        if not field.data:
            return
        normalized_email = field.data.strip().lower()
        if User.query.filter_by(email=normalized_email).first():
            raise ValidationError("An account with this email address already exists. Please log in.")


class LoginForm(FlaskForm):
    """User authentication form."""
    email = StringField(
        'Email Address',
        validators=[
            DataRequired(message="Email address is required."),
            Email(message="Please enter a valid email address.")
        ],
        render_kw={"placeholder": "you@college.edu"}
    )
    password = PasswordField(
        'Password',
        validators=[DataRequired(message="Password is required.")],
        render_kw={"placeholder": "••••••••"}
    )
    remember_me = BooleanField('Remember Me')
    submit = SubmitField('Sign In')


class EventForm(FlaskForm):
    """Form for administrators to create or edit events."""
    title = StringField(
        'Event Title',
        validators=[
            DataRequired(message="Event title is required."),
            Length(min=3, max=150, message="Title must be between 3 and 150 characters.")
        ],
        render_kw={"placeholder": "e.g., Annual Hackathon 2026"}
    )
    category = SelectField(
        'Category',
        choices=[(cat, cat) for cat in Event.CATEGORIES],
        validators=[DataRequired(message="Please select a category.")]
    )
    description = TextAreaField(
        'Event Description',
        validators=[
            DataRequired(message="Description is required."),
            Length(min=10, message="Description must be at least 10 characters long.")
        ],
        render_kw={"rows": 5, "placeholder": "Provide details regarding the agenda, schedule, requirements, and prizes..."}
    )
    venue = StringField(
        'Venue / Location',
        validators=[
            DataRequired(message="Venue is required."),
            Length(min=3, max=150, message="Venue must be between 3 and 150 characters.")
        ],
        render_kw={"placeholder": "e.g., Main Auditorium / Lab 304"}
    )
    event_date = DateField(
        'Event Date',
        validators=[DataRequired(message="Event date is required.")],
        format='%Y-%m-%d'
    )
    start_time = TimeField(
        'Start Time',
        validators=[DataRequired(message="Start time is required.")],
        format=['%H:%M', '%H:%M:%S']
    )
    capacity = IntegerField(
        'Total Seat Capacity',
        validators=[
            DataRequired(message="Capacity is required."),
            NumberRange(min=1, max=10000, message="Capacity must be at least 1 seat.")
        ],
        render_kw={"placeholder": "e.g., 100"}
    )
    submit = SubmitField('Save Event')


class EmptyForm(FlaskForm):
    """Empty form used to validate CSRF tokens for state-changing POST buttons."""
    pass
