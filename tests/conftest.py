import pytest
from datetime import date, time, timedelta, datetime
from app import create_app
from app.extensions import db
from app.models import User, Event, Registration, Notification
from config import TestConfig

@pytest.fixture
def app():
    app = create_app(TestConfig)
    with app.app_context():
        db.create_all()
        yield app
        db.session.remove()
        db.drop_all()

@pytest.fixture
def client(app):
    return app.test_client()

@pytest.fixture
def runner(app):
    return app.test_cli_runner()

@pytest.fixture
def seed_users(app):
    with app.app_context():
        admin = User(name="Admin User", email="admin@test.edu", role="admin")
        admin.set_password("Admin@123")

        organizer1 = User(name="Org One", email="org1@test.edu", role="organizer")
        organizer1.set_password("Org@123")

        organizer2 = User(name="Org Two", email="org2@test.edu", role="organizer")
        organizer2.set_password("Org@123")

        student1 = User(name="Student One", email="student1@test.edu", role="student", department="CSE", year="3rd Year")
        student1.set_password("Student@123")

        student2 = User(name="Student Two", email="student2@test.edu", role="student", department="IT", year="2nd Year")
        student2.set_password("Student@123")

        db.session.add_all([admin, organizer1, organizer2, student1, student2])
        db.session.commit()

        return {
            "admin": admin,
            "organizer1": organizer1,
            "organizer2": organizer2,
            "student1": student1,
            "student2": student2
        }

@pytest.fixture
def sample_event(app, seed_users):
    with app.app_context():
        org = User.query.filter_by(email="org1@test.edu").first()
        today = date.today()
        event = Event(
            title="AI Hackathon 2026",
            description="Testing AI Hackathon event description with over 20 characters.",
            category="Technical",
            event_date=today + timedelta(days=10),
            start_time=time(10, 0),
            end_time=time(18, 0),
            venue="CS Seminar Hall",
            capacity=2, # Small capacity to test capacity limits
            registration_deadline=today + timedelta(days=8),
            eligibility="All Students",
            contact_email="org1@test.edu",
            organizer_id=org.id,
            approval_status="approved"
        )
        db.session.add(event)
        db.session.commit()
        return event.id
