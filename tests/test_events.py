from datetime import date, time, timedelta
from app.models import Event
from app.extensions import db


def test_homepage_response(client):
    """Verify homepage loads with branding and status code 200."""
    response = client.get('/')
    assert response.status_code == 200
    assert b"CampusConnect" in response.data
    assert b"Your Campus. Your Community." in response.data


def test_about_page_response(client):
    """Verify about page loads successfully."""
    response = client.get('/about')
    assert response.status_code == 200
    assert b"CampusConnect Architecture" in response.data
    assert b"Technology Stack" in response.data


def test_events_listing_and_filter(client, sample_event):
    """Verify event browsing, search query, and category filters."""
    # General listing
    response = client.get('/events')
    assert response.status_code == 200
    assert b"AI and Machine Learning Symposium" in response.data

    # Category filter match
    cat_match = client.get('/events?category=Seminar')
    assert cat_match.status_code == 200
    assert b"AI and Machine Learning Symposium" in cat_match.data

    # Category filter mismatch
    cat_mismatch = client.get('/events?category=Sports')
    assert cat_mismatch.status_code == 200
    assert b"AI and Machine Learning Symposium" not in cat_mismatch.data

    # Search keyword match
    search_resp = client.get('/events?q=Machine+Learning')
    assert search_resp.status_code == 200
    assert b"AI and Machine Learning Symposium" in search_resp.data


def test_event_detail_page(client, sample_event):
    """Verify individual event detail page rendering."""
    response = client.get(f'/events/{sample_event.id}')
    assert response.status_code == 200
    assert b"AI and Machine Learning Symposium" in response.data
    assert b"Main Auditorium Block A" in response.data


def test_invalid_event_id_404(client):
    """Verify requesting a non-existent event triggers a 404 page."""
    response = client.get('/events/99999')
    assert response.status_code == 404
    assert b"Page Not Found" in response.data


def test_admin_create_event(client, admin_user, app):
    """Verify that administrators can create new campus events."""
    # Login as admin
    client.post('/login', data={'email': 'admin@college.edu', 'password': 'Admin@123'})

    event_date = date.today() + timedelta(days=12)
    response = client.post('/admin/events/create', data={
        'title': 'Autonomous Drone Workshop',
        'category': 'Workshop',
        'venue': 'Robotics Lab 102',
        'event_date': event_date.strftime('%Y-%m-%d'),
        'start_time': '14:30',
        'capacity': 45,
        'description': 'Comprehensive hands-on workshop covering flight controllers, telemetry, and automated obstacle avoidance.'
    }, follow_redirects=True)

    assert response.status_code == 200
    assert b"Autonomous Drone Workshop" in response.data

    with app.app_context():
        created = Event.query.filter_by(title='Autonomous Drone Workshop').first()
        assert created is not None
        assert created.capacity == 45
        assert created.category == 'Workshop'


def test_admin_edit_event(client, admin_user, sample_event, app):
    """Verify admin can update event details and venue."""
    client.post('/login', data={'email': 'admin@college.edu', 'password': 'Admin@123'})

    response = client.post(f'/admin/events/{sample_event.id}/edit', data={
        'title': 'AI Symposium: Updated Edition',
        'category': 'Seminar',
        'venue': 'New Technology Auditorium Block C',
        'event_date': sample_event.event_date.strftime('%Y-%m-%d'),
        'start_time': '11:00',
        'capacity': 100,
        'description': sample_event.description
    }, follow_redirects=True)

    assert response.status_code == 200
    assert b"updated successfully" in response.data

    with app.app_context():
        updated = db.session.get(Event, sample_event.id)
        assert updated.title == 'AI Symposium: Updated Edition'
        assert updated.venue == 'New Technology Auditorium Block C'
        assert updated.capacity == 100


def test_admin_delete_event(client, admin_user, sample_event, app):
    """Verify admin can delete an event."""
    client.post('/login', data={'email': 'admin@college.edu', 'password': 'Admin@123'})

    response = client.post(f'/admin/events/{sample_event.id}/delete', follow_redirects=True)
    assert response.status_code == 200
    assert b"were removed" in response.data

    with app.app_context():
        deleted = db.session.get(Event, sample_event.id)
        assert deleted is None


def test_student_cannot_create_event(client, student_user):
    """Verify students are forbidden from creating events."""
    client.post('/login', data={'email': 'aarav@college.edu', 'password': 'Student@123'})

    response = client.get('/admin/events/create')
    assert response.status_code == 403
