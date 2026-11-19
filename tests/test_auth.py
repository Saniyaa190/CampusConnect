from app.models import User
from app.extensions import db


def test_password_hashing(app):
    """Test password hashing and verification security."""
    u = User(full_name="Test Student", email="test@college.edu")
    u.set_password("SecurePass123!")
    assert u.password_hash != "SecurePass123!"
    assert u.check_password("SecurePass123!") is True
    assert u.check_password("WrongPassword") is False


def test_signup_page_loads(client):
    """Verify signup page renders successfully."""
    response = client.get('/signup')
    assert response.status_code == 200
    assert b"Create Student Account" in response.data


def test_student_signup_success(client, app):
    """Verify that a student can register an account successfully."""
    response = client.post('/signup', data={
        'full_name': 'Rohan Sen',
        'email': 'rohan@college.edu',
        'password': 'Password@123',
        'confirm_password': 'Password@123'
    }, follow_redirects=True)

    assert response.status_code == 200
    assert b"Account created successfully" in response.data

    with app.app_context():
        user = User.query.filter_by(email='rohan@college.edu').first()
        assert user is not None
        assert user.full_name == 'Rohan Sen'
        assert user.role == 'STUDENT'
        assert user.check_password('Password@123') is True


def test_duplicate_email_rejected(client, student_user):
    """Verify system rejects registration with an existing email."""
    response = client.post('/signup', data={
        'full_name': 'Another User',
        'email': 'aarav@college.edu',  # Existing fixture email
        'password': 'Password@123',
        'confirm_password': 'Password@123'
    })
    assert response.status_code == 200
    assert b"already exists" in response.data


def test_login_page_loads(client):
    """Verify login page renders successfully."""
    response = client.get('/login')
    assert response.status_code == 200
    assert b"Welcome Back" in response.data


def test_student_login_and_logout(client, student_user):
    """Verify student login redirects to dashboard and logout clears session."""
    # Login
    response = client.post('/login', data={
        'email': 'aarav@college.edu',
        'password': 'Student@123'
    }, follow_redirects=True)

    assert response.status_code == 200
    assert b"Welcome back, Aarav Sharma!" in response.data
    assert b"Student Hub" in response.data

    # Logout
    logout_resp = client.get('/logout', follow_redirects=True)
    assert logout_resp.status_code == 200
    assert b"signed out successfully" in logout_resp.data


def test_admin_login_redirect(client, admin_user):
    """Verify admin login redirects automatically to admin dashboard."""
    response = client.post('/login', data={
        'email': 'admin@college.edu',
        'password': 'Admin@123'
    }, follow_redirects=True)

    assert response.status_code == 200
    assert b"Administrator Console" in response.data


def test_invalid_login_credentials(client, student_user):
    """Verify rejection of invalid login password."""
    response = client.post('/login', data={
        'email': 'aarav@college.edu',
        'password': 'IncorrectPassword'
    }, follow_redirects=True)

    assert response.status_code == 200
    assert b"Invalid email or password" in response.data


def test_role_authorization_protection(client, student_user):
    """Verify students cannot access administrative dashboard (403 forbidden)."""
    # Log in as student
    client.post('/login', data={
        'email': 'aarav@college.edu',
        'password': 'Student@123'
    })

    # Try to access admin dashboard
    response = client.get('/admin/dashboard')
    assert response.status_code == 403
    assert b"Access Forbidden" in response.data
