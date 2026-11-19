from datetime import date, time, timedelta
from app.models import User, Event, Registration
from app.extensions import db


def test_student_can_register_for_event(client, student_user, sample_event, app):
    """Verify student can successfully register for an upcoming event."""
    client.post('/login', data={'email': 'aarav@college.edu', 'password': 'Student@123'})

    response = client.post(f'/events/{sample_event.id}/register', follow_redirects=True)
    assert response.status_code == 200
    assert b"You have officially registered" in response.data

    with app.app_context():
        event = db.session.get(Event, sample_event.id)
        assert event.active_registrations_count == 1
        assert event.available_seats == 1
        user = db.session.get(User, student_user.id)
        assert user.is_registered_for(event.id) is True


def test_duplicate_registration_prevented(client, student_user, sample_event):
    """Verify system prevents duplicate active registrations from the same student."""
    client.post('/login', data={'email': 'aarav@college.edu', 'password': 'Student@123'})

    # First registration
    client.post(f'/events/{sample_event.id}/register')

    # Attempt second registration
    second_resp = client.post(f'/events/{sample_event.id}/register', follow_redirects=True)
    assert second_resp.status_code == 200
    assert b"already registered" in second_resp.data


def test_capacity_limit_enforced(client, student_user, sample_event, app):
    """Verify that when an event reaches maximum capacity, further registrations are blocked."""
    # sample_event has capacity=2
    with app.app_context():
        # Add two registered users to exhaust capacity
        u1 = User(full_name="Student One", email="s1@college.edu", role="STUDENT")
        u1.set_password("Pass@123")
        u2 = User(full_name="Student Two", email="s2@college.edu", role="STUDENT")
        u2.set_password("Pass@123")
        db.session.add_all([u1, u2])
        db.session.commit()

        r1 = Registration(user_id=u1.id, event_id=sample_event.id, status='REGISTERED')
        r2 = Registration(user_id=u2.id, event_id=sample_event.id, status='REGISTERED')
        db.session.add_all([r1, r2])
        db.session.commit()

    # Now student_user attempts to register for fully booked event
    client.post('/login', data={'email': 'aarav@college.edu', 'password': 'Student@123'})
    response = client.post(f'/events/{sample_event.id}/register', follow_redirects=True)

    assert response.status_code == 200
    assert b"fully booked" in response.data


def test_past_event_registration_rejected(client, student_user, admin_user, app):
    """Verify students cannot register for past events."""
    with app.app_context():
        past_event = Event(
            title="Past Coding Competition",
            category="Technology",
            description="Event held last month.",
            venue="Old Auditorium",
            event_date=date.today() - timedelta(days=10),
            start_time=time(10, 0),
            capacity=50,
            created_by=admin_user.id
        )
        db.session.add(past_event)
        db.session.commit()
        past_event_id = past_event.id

    client.post('/login', data={'email': 'aarav@college.edu', 'password': 'Student@123'})
    response = client.post(f'/events/{past_event_id}/register', follow_redirects=True)

    assert response.status_code == 200
    assert b"already taken place" in response.data


def test_student_can_cancel_registration(client, student_user, sample_event, app):
    """Verify student can cancel active registration and replenish seat capacity."""
    client.post('/login', data={'email': 'aarav@college.edu', 'password': 'Student@123'})

    # Register first
    client.post(f'/events/{sample_event.id}/register')

    # Cancel registration
    cancel_resp = client.post(f'/events/{sample_event.id}/cancel', follow_redirects=True)
    assert cancel_resp.status_code == 200
    assert b"has been cancelled" in cancel_resp.data

    with app.app_context():
        event = db.session.get(Event, sample_event.id)
        assert event.active_registrations_count == 0
        assert event.available_seats == 2
        user = db.session.get(User, student_user.id)
        assert user.is_registered_for(event.id) is False


def test_admin_event_participants_view(client, admin_user, student_user, sample_event):
    """Verify administrator can inspect the student participant roster."""
    # Student registers
    client.post('/login', data={'email': 'aarav@college.edu', 'password': 'Student@123'})
    client.post(f'/events/{sample_event.id}/register')
    client.get('/logout')

    # Admin logs in
    client.post('/login', data={'email': 'admin@college.edu', 'password': 'Admin@123'})
    response = client.get(f'/admin/events/{sample_event.id}/registrations')

    assert response.status_code == 200
    assert b"Participant Roster" in response.data
    assert b"Aarav Sharma" in response.data
    assert b"aarav@college.edu" in response.data


def test_cancel_redirects_to_referrer_dashboard(client, student_user, sample_event):
    """Verify that cancelling from dashboard redirects back to student dashboard."""
    client.post('/login', data={'email': 'aarav@college.edu', 'password': 'Student@123'})
    client.post(f'/events/{sample_event.id}/register')

    # Cancel with dashboard as referrer
    response = client.post(
        f'/events/{sample_event.id}/cancel',
        headers={'Referer': 'http://localhost/student/dashboard'},
        follow_redirects=True
    )
    assert response.status_code == 200
    assert b"Student Hub" in response.data
    assert b"has been cancelled" in response.data


def test_cancel_redirects_to_referrer_registrations(client, student_user, sample_event):
    """Verify that cancelling from registrations table redirects back to registrations."""
    client.post('/login', data={'email': 'aarav@college.edu', 'password': 'Student@123'})
    client.post(f'/events/{sample_event.id}/register')

    # Cancel with registrations as referrer
    response = client.post(
        f'/events/{sample_event.id}/cancel',
        headers={'Referer': 'http://localhost/student/registrations'},
        follow_redirects=True
    )
    assert response.status_code == 200
    assert b"My Event Registrations" in response.data
    assert b"has been cancelled" in response.data
