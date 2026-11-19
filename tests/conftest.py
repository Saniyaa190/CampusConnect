from datetime import date, time, timedelta
import pytest
from app import create_app
from app.extensions import db
from app.models import User, Event, Registration


@pytest.fixture
def app():
    """Create and configure an isolated application instance for testing."""
    test_app = create_app('testing')

    with test_app.app_context():
        db.create_all()
        yield test_app
        db.session.remove()
        db.drop_all()


@pytest.fixture
def client(app):
    """Test client for issuing HTTP requests."""
    return app.test_client()


@pytest.fixture
def runner(app):
    """CLI test runner."""
    return app.test_cli_runner()


@pytest.fixture
def student_user(app):
    """Create a test student user."""
    with app.app_context():
        user = User(
            full_name="Aarav Sharma",
            email="aarav@college.edu",
            role="STUDENT"
        )
        user.set_password("Student@123")
        db.session.add(user)
        db.session.commit()
        # Refresh and make persistent without expiring
        db.session.refresh(user)
        db.session.expunge(user)
        return user


@pytest.fixture
def admin_user(app):
    """Create a test administrator user."""
    with app.app_context():
        admin = User(
            full_name="Dr. Rajiv Mehta",
            email="admin@college.edu",
            role="ADMIN"
        )
        admin.set_password("Admin@123")
        db.session.add(admin)
        db.session.commit()
        db.session.refresh(admin)
        db.session.expunge(admin)
        return admin


@pytest.fixture
def sample_event(app, admin_user):
    """Create a sample event for testing."""
    with app.app_context():
        event = Event(
            title="AI and Machine Learning Symposium",
            category="Seminar",
            description="A comprehensive conference showcasing deep learning innovations and industrial computer vision applications.",
            venue="Main Auditorium Block A",
            event_date=date.today() + timedelta(days=7),
            start_time=time(10, 0),
            capacity=2,  # Intentionally small capacity to test limits
            created_by=admin_user.id
        )
        db.session.add(event)
        db.session.commit()
        db.session.refresh(event)
        db.session.expunge(event)
        return event
