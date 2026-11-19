from datetime import date, time, timedelta
from app.models import User, Event, Registration
from app.extensions import db


def test_full_student_and_admin_workflow(client, app):
    """End-to-end user journey test: student registration, booking, cancellation, admin CRUD."""
    with app.app_context():
        # 1. Student Signup
        resp = client.post('/signup', data={
            'full_name': 'Priya Patel',
            'email': 'priya@college.edu',
            'password': 'SecurePass@123',
            'confirm_password': 'SecurePass@123'
        }, follow_redirects=True)
        assert resp.status_code == 200
        assert b"Account created successfully" in resp.data

        # 2. Student Login
        resp = client.post('/login', data={
            'email': 'priya@college.edu',
            'password': 'SecurePass@123'
        }, follow_redirects=True)
        assert resp.status_code == 200
        assert b"Student Hub" in resp.data

        # 3. Create Admin & Event in context
        admin = User(full_name='Prof. Sharma', email='admin@campus.edu', role='ADMIN')
        admin.set_password('AdminSecret@123')
        db.session.add(admin)
        db.session.commit()

        ev = Event(
            title="Robotics and AI Showcase",
            category="Technology",
            description="Demonstration of autonomous drones, telemetry systems, and robotic arms.",
            venue="Auditorium Block C",
            event_date=date.today() + timedelta(days=5),
            start_time=time(14, 0),
            capacity=10,
            created_by=admin.id
        )
        db.session.add(ev)
        db.session.commit()
        ev_id = ev.id

    # 4. Student views event details
    resp = client.get(f'/events/{ev_id}')
    assert resp.status_code == 200
    assert b"Robotics and AI Showcase" in resp.data

    # 5. Student registers for event
    resp = client.post(f'/events/{ev_id}/register', follow_redirects=True)
    assert resp.status_code == 200
    assert b"You have officially registered" in resp.data

    # 6. Check Student Dashboard & Registrations table
    resp = client.get('/student/dashboard')
    assert resp.status_code == 200
    assert b"Robotics and AI Showcase" in resp.data

    resp = client.get('/student/registrations')
    assert resp.status_code == 200
    assert b"Robotics and AI Showcase" in resp.data

    # 7. Cancel registration
    resp = client.post(f'/events/{ev_id}/cancel', follow_redirects=True)
    assert resp.status_code == 200
    assert b"has been cancelled" in resp.data

    # 8. Student logout
    resp = client.get('/logout', follow_redirects=True)
    assert resp.status_code == 200

    # 9. Admin Login & Operations
    resp = client.post('/login', data={
        'email': 'admin@campus.edu',
        'password': 'AdminSecret@123'
    }, follow_redirects=True)
    assert resp.status_code == 200
    assert b"Administrator Console" in resp.data

    # 10. Admin views roster
    resp = client.get(f'/admin/events/{ev_id}/registrations')
    assert resp.status_code == 200
    assert b"Participant Roster" in resp.data

    # 11. Admin edits event
    resp = client.post(f'/admin/events/{ev_id}/edit', data={
        'title': 'Robotics and AI Showcase - Updated',
        'category': 'Technology',
        'description': 'Updated description.',
        'venue': 'Auditorium Block C',
        'event_date': (date.today() + timedelta(days=6)).strftime('%Y-%m-%d'),
        'start_time': '15:00',
        'capacity': 15
    }, follow_redirects=True)
    assert resp.status_code == 200
    assert b"updated successfully" in resp.data

    # 12. Admin deletes event
    resp = client.post(f'/admin/events/{ev_id}/delete', follow_redirects=True)
    assert resp.status_code == 200
    assert b"were removed" in resp.data
