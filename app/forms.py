from datetime import date
from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed
from wtforms import StringField, PasswordField, SubmitField, BooleanField, SelectField, TextAreaField, IntegerField, DateField, TimeField
from wtforms.validators import DataRequired, Email, Length, EqualTo, ValidationError, NumberRange, Optional
from flask_login import current_user
from app.models import User

EVENT_CATEGORIES = [
    ("Technical", "Technical"),
    ("Cultural", "Cultural"),
    ("Sports", "Sports"),
    ("Workshops", "Workshops"),
    ("Seminars", "Seminars"),
    ("Competitions", "Competitions"),
    ("Other", "Other")
]

DEPARTMENTS = [
    ("Computer Science & Engineering", "Computer Science & Engineering"),
    ("Information Technology", "Information Technology"),
    ("Electronics & Communication", "Electronics & Communication"),
    ("Electrical Engineering", "Electrical Engineering"),
    ("Mechanical Engineering", "Mechanical Engineering"),
    ("Civil Engineering", "Civil Engineering"),
    ("Business Administration (MBA/BBA)", "Business Administration (MBA/BBA)"),
    ("Applied Sciences & Humanities", "Applied Sciences & Humanities"),
    ("Other", "Other")
]

STUDY_YEARS = [
    ("1st Year", "1st Year"),
    ("2nd Year", "2nd Year"),
    ("3rd Year", "3rd Year"),
    ("4th Year", "4th Year"),
    ("Postgraduate", "Postgraduate"),
    ("Faculty / Staff", "Faculty / Staff")
]

class LoginForm(FlaskForm):
    email = StringField("Email Address", validators=[DataRequired(), Email()])
    password = PasswordField("Password", validators=[DataRequired()])
    remember = BooleanField("Remember Me")
    submit = SubmitField("Sign In")


class RegisterForm(FlaskForm):
    name = StringField("Full Name", validators=[DataRequired(), Length(min=2, max=100)])
    email = StringField("College Email", validators=[DataRequired(), Email(), Length(max=150)])
    role = SelectField("Register As", choices=[("student", "Student"), ("organizer", "Event Organizer")], default="student")
    department = SelectField("Department", choices=DEPARTMENTS, default="Computer Science & Engineering")
    year = SelectField("Academic Year", choices=STUDY_YEARS, default="1st Year")
    password = PasswordField("Password", validators=[DataRequired(), Length(min=6, message="Password must be at least 6 characters.")])
    confirm_password = PasswordField("Confirm Password", validators=[DataRequired(), EqualTo("password", message="Passwords must match.")])
    submit = SubmitField("Create Account")

    def validate_email(self, email):
        user = User.query.filter_by(email=email.data.strip().lower()).first()
        if user:
            raise ValidationError("An account with this email already exists.")


class ProfileForm(FlaskForm):
    name = StringField("Full Name", validators=[DataRequired(), Length(min=2, max=100)])
    department = SelectField("Department", choices=DEPARTMENTS)
    year = SelectField("Academic Year", choices=STUDY_YEARS)
    current_password = PasswordField("Current Password", validators=[Optional()])
    new_password = PasswordField("New Password (leave blank to keep current)", validators=[Optional(), Length(min=6)])
    confirm_new_password = PasswordField("Confirm New Password", validators=[Optional(), EqualTo("new_password", message="New passwords must match.")])
    submit = SubmitField("Save Profile")


class EventForm(FlaskForm):
    title = StringField("Event Title", validators=[DataRequired(), Length(min=4, max=200)])
    category = SelectField("Category", choices=EVENT_CATEGORIES, default="Technical")
    description = TextAreaField("Description", validators=[DataRequired(), Length(min=20)])
    event_date = DateField("Event Date", validators=[DataRequired()], format="%Y-%m-%d")
    start_time = TimeField("Start Time", validators=[DataRequired()], format="%H:%M")
    end_time = TimeField("End Time", validators=[DataRequired()], format="%H:%M")
    venue = StringField("Venue / Location", validators=[DataRequired(), Length(min=3, max=150)])
    capacity = IntegerField("Maximum Capacity (Participants)", validators=[DataRequired(), NumberRange(min=1, max=10000)], default=100)
    registration_deadline = DateField("Registration Deadline", validators=[DataRequired()], format="%Y-%m-%d")
    eligibility = StringField("Eligibility Criteria", validators=[DataRequired(), Length(max=150)], default="Open to all students")
    contact_email = StringField("Organizer Contact Email", validators=[DataRequired(), Email(), Length(max=150)])
    image = FileField("Event Cover Image", validators=[
        Optional(),
        FileAllowed(["jpg", "jpeg", "png", "webp", "gif"], "Images only (.jpg, .jpeg, .png, .webp, .gif)")
    ])
    submit = SubmitField("Submit Event")

    def validate_event_date(self, field):
        if field.data and field.data < date.today():
            raise ValidationError("Event date cannot be in the past.")

    def validate_registration_deadline(self, field):
        if field.data and self.event_date.data:
            if field.data > self.event_date.data:
                raise ValidationError("Registration deadline must be on or before the event date.")
            if field.data < date.today():
                raise ValidationError("Registration deadline cannot be in the past.")

    def validate_end_time(self, field):
        if self.start_time.data and field.data:
            if self.event_date.data == date.today():
                pass
            if field.data <= self.start_time.data:
                raise ValidationError("End time must be after the start time.")
