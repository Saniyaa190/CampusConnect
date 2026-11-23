from datetime import date, time, timedelta
from flask_login import login_user
from app.extensions import db
from app.models import User, Event, Registration, Notification

def login_test_user(client, email, password):
    return client.post("/auth/login", data={
        "email": email,
        "password": password
    }, follow_redirects=True)

def logout_test_user(client):
    return client.get("/auth/logout", follow_redirects=True)


# 1. User Registration
def test_user_registration(client, app):
    response = client.post("/auth/register", data={
        "name": "New Student",
        "email": "newstudent@test.edu",
        "role": "student",
        "department": "Computer Science & Engineering",
        "year": "1st Year",
        "password": "Password123",
        "confirm_password": "Password123"
    }, follow_redirects=True)

    assert response.status_code == 200
    with app.app_context():
        user = User.query.filter_by(email="newstudent@test.edu").first()
        assert user is not None
        assert user.name == "New Student"
        assert user.role == "student"
        assert user.check_password("Password123")
        assert not user.check_password("WrongPassword")


# 2. User Login
def test_user_login_success(client, seed_users):
    response = login_test_user(client, "student1@test.edu", "Student@123")
    assert response.status_code == 200
    assert b"Welcome back, Student One" in response.data or b"Student Portal" in response.data


# 3. Invalid Login
def test_user_login_invalid(client, seed_users):
    response = login_test_user(client, "student1@test.edu", "IncorrectPass")
    assert response.status_code == 200
    assert b"Invalid email or password" in response.data


# 4. Role-Based Access Control
def test_role_based_access_student_denied_admin(client, seed_users):
    # Log in as student
    login_test_user(client, "student1@test.edu", "Student@123")
    # Try accessing admin dashboard
    response = client.get("/admin/dashboard", follow_redirects=True)
    assert response.status_code == 200
    # Must be redirected with access denied
    assert b"Access denied" in response.data or b"Student Portal" in response.data


def test_role_based_access_unauthenticated_denied(client):
    response = client.get("/student/dashboard", follow_redirects=True)
    assert response.status_code == 200
    assert b"Please log in to" in response.data or b"Sign In" in response.data


# 5. Event Creation (Starts in Pending Status)
def test_event_creation(client, app, seed_users):
    login_test_user(client, "org1@test.edu", "Org@123")
    today = date.today()
    
    response = client.post("/organizer/events/create", data={
        "title": "Robotics Design Competition",
        "category": "Competitions",
        "description": "A very detailed description of the robotics design challenge with rules and judging criteria.",
        "event_date": (today + timedelta(days=15)).strftime("%Y-%m-%d"),
        "start_time": "10:00",
        "end_time": "16:00",
        "venue": "Robotics Lab Room 101",
        "capacity": 50,
        "registration_deadline": (today + timedelta(days=12)).strftime("%Y-%m-%d"),
        "eligibility": "All Students",
        "contact_email": "org1@test.edu"
    }, follow_redirects=True)

    assert response.status_code == 200
    with app.app_context():
        ev = Event.query.filter_by(title="Robotics Design Competition").first()
        assert ev is not None
        assert ev.approval_status == "pending"
        assert ev.capacity == 50


# 6. Event Editing
def test_event_editing(client, app, seed_users, sample_event):
    login_test_user(client, "org1@test.edu", "Org@123")
    today = date.today()

    response = client.post(f"/organizer/events/{sample_event}/edit", data={
        "title": "AI Hackathon 2026 - Updated Edition",
        "category": "Technical",
        "description": "Updated event description testing over 20 characters in length for form validation.",
        "event_date": (today + timedelta(days=10)).strftime("%Y-%m-%d"),
        "start_time": "10:00",
        "end_time": "18:00",
        "venue": "Main Hall Auditorium",
        "capacity": 2,
        "registration_deadline": (today + timedelta(days=8)).strftime("%Y-%m-%d"),
        "eligibility": "All Students",
        "contact_email": "org1@test.edu"
    }, follow_redirects=True)

    assert response.status_code == 200
    with app.app_context():
        ev = db.session.get(Event, sample_event)
        assert ev.title == "AI Hackathon 2026 - Updated Edition"
        assert ev.venue == "Main Hall Auditorium"


# 7. Unauthorized Event Editing (Organizer 2 cannot edit Organizer 1's event)
def test_unauthorized_event_editing(client, seed_users, sample_event):
    login_test_user(client, "org2@test.edu", "Org@123")
    response = client.get(f"/organizer/events/{sample_event}/edit")
    assert response.status_code in [403, 302]


# 8. Event Approval by Admin
def test_event_approval(client, app, seed_users):
    # Create pending event
    with app.app_context():
        org = User.query.filter_by(email="org1@test.edu").first()
        today = date.today()
        ev = Event(
            title="Pending Cultural Night",
            description="Cultural night dance performances and vocal competitions.",
            category="Cultural",
            event_date=today + timedelta(days=20),
            start_time=time(18, 0),
            end_time=time(22, 0),
            venue="Amphitheater",
            capacity=200,
            registration_deadline=today + timedelta(days=18),
            eligibility="All Students",
            contact_email="org1@test.edu",
            organizer_id=org.id,
            approval_status="pending"
        )
        db.session.add(ev)
        db.session.commit()
        ev_id = ev.id

    # Admin approves
    login_test_user(client, "admin@test.edu", "Admin@123")
    response = client.post(f"/admin/events/{ev_id}/approve", follow_redirects=True)
    assert response.status_code == 200

    with app.app_context():
        approved_ev = db.session.get(Event, ev_id)
        assert approved_ev.approval_status == "approved"


# 9. Event Registration by Student
def test_event_registration(client, app, seed_users, sample_event):
    login_test_user(client, "student1@test.edu", "Student@123")
    response = client.post(f"/events/{sample_event}/register", follow_redirects=True)
    assert response.status_code == 200
    assert b"successfully registered" in response.data

    with app.app_context():
        st = User.query.filter_by(email="student1@test.edu").first()
        reg = Registration.query.filter_by(student_id=st.id, event_id=sample_event).first()
        assert reg is not None
        assert reg.registration_status == "confirmed"


# 10. Duplicate Registration Prevention
def test_duplicate_registration_prevention(client, seed_users, sample_event):
    login_test_user(client, "student1@test.edu", "Student@123")
    # First registration
    client.post(f"/events/{sample_event}/register", follow_redirects=True)
    # Second attempt
    response = client.post(f"/events/{sample_event}/register", follow_redirects=True)
    assert b"already registered" in response.data


# 11. Event Capacity Restrictions
def test_event_capacity_restrictions(client, app, seed_users, sample_event):
    # Capacity is 2
    # Register student 1
    login_test_user(client, "student1@test.edu", "Student@123")
    client.post(f"/events/{sample_event}/register", follow_redirects=True)
    logout_test_user(client)

    # Register student 2
    login_test_user(client, "student2@test.edu", "Student@123")
    client.post(f"/events/{sample_event}/register", follow_redirects=True)
    logout_test_user(client)

    # Attempt to register 3rd student
    with app.app_context():
        student3 = User(name="Student Three", email="student3@test.edu", role="student")
        student3.set_password("Student@123")
        db.session.add(student3)
        db.session.commit()

    login_test_user(client, "student3@test.edu", "Student@123")
    response = client.post(f"/events/{sample_event}/register", follow_redirects=True)
    assert b"full capacity" in response.data


# 12. Registration Cancellation
def test_registration_cancellation(client, app, seed_users, sample_event):
    login_test_user(client, "student1@test.edu", "Student@123")
    # Register
    client.post(f"/events/{sample_event}/register", follow_redirects=True)
    # Cancel
    response = client.post(f"/events/{sample_event}/cancel", follow_redirects=True)
    assert response.status_code == 200
    assert b"cancelled" in response.data

    with app.app_context():
        st = User.query.filter_by(email="student1@test.edu").first()
        reg = Registration.query.filter_by(student_id=st.id, event_id=sample_event).first()
        assert reg.registration_status == "cancelled"


# 13. Unauthorized Role Actions
def test_unauthorized_student_access(client, seed_users):
    login_test_user(client, "student1@test.edu", "Student@123")
    response = client.get("/organizer/events/create", follow_redirects=True)
    assert response.status_code == 200
    assert b"Access denied" in response.data


# 14. Notifications Flow
def test_notification_flow(client, app, seed_users):
    with app.app_context():
        st = User.query.filter_by(email="student1@test.edu").first()
        notif = Notification(
            user_id=st.id,
            title="Important Alert",
            message="Test alert message",
            is_read=False
        )
        db.session.add(notif)
        db.session.commit()
        notif_id = notif.id

    login_test_user(client, "student1@test.edu", "Student@123")
    response = client.post(f"/notifications/{notif_id}/read", follow_redirects=True)
    assert response.status_code == 200

    with app.app_context():
        updated_n = db.session.get(Notification, notif_id)
        assert updated_n.is_read is True
