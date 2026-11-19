import os
from datetime import datetime, date, time, timedelta, timezone
import click
import pymysql
from flask import Flask, render_template
from app.extensions import db, migrate, login_manager, csrf
from config import config_by_name


def test_mysql_connectivity(host, port, user, password, db_name):
    """Test whether MySQL is reachable with provided credentials."""
    try:
        conn = pymysql.connect(
            host=host,
            port=int(port),
            user=user,
            password=password,
            database=db_name,
            connect_timeout=2
        )
        conn.close()
        return True, "Connected successfully"
    except Exception as e:
        return False, str(e)


def create_app(config_name='default'):
    """Application factory for CampusConnect."""
    app = Flask(__name__, template_folder='templates', static_folder='static')

    # Load configuration
    config_obj = config_by_name.get(config_name, config_by_name['default'])
    app.config.from_object(config_obj)

    # Ensure instance folder exists
    os.makedirs(app.instance_path, exist_ok=True)

    # Verify and configure database engine before initializing SQLAlchemy
    if not app.config.get('TESTING'):
        db_uri = app.config.get('SQLALCHEMY_DATABASE_URI', '')
        if db_uri.startswith('mysql'):
            host = app.config.get('DB_HOST', 'localhost')
            port = app.config.get('DB_PORT', 3306)
            user = app.config.get('DB_USERNAME', 'root')
            password = app.config.get('DB_PASSWORD', '')
            db_name = app.config.get('DB_NAME', 'campusconnect')

            can_connect, err_msg = test_mysql_connectivity(host, port, user, password, db_name)
            if not can_connect:
                if app.config.get('ALLOW_SQLITE_FALLBACK', True):
                    sqlite_path = os.path.join(app.instance_path, 'campusconnect.db')
                    app.logger.warning(
                        f"MySQL connection unavailable ({err_msg}). Falling back to local SQLite: {sqlite_path}"
                    )
                    app.config['SQLALCHEMY_DATABASE_URI'] = f"sqlite:///{sqlite_path}"
                    app.config['SQLALCHEMY_ENGINE_OPTIONS'] = {}
                else:
                    app.logger.error(f"MySQL connection error: {err_msg}")

    # Initialize extensions
    db.init_app(app)
    migrate.init_app(app, db)
    login_manager.init_app(app)
    csrf.init_app(app)

    # Register Blueprints
    from app.main import main_bp
    from app.auth import auth_bp
    from app.events import events_bp
    from app.student import student_bp
    from app.admin import admin_bp

    app.register_blueprint(main_bp)
    app.register_blueprint(auth_bp)
    app.register_blueprint(events_bp)
    app.register_blueprint(student_bp)
    app.register_blueprint(admin_bp)

    # Register Custom Error Handlers
    @app.errorhandler(403)
    def forbidden_error(error):
        return render_template('errors/403.html', title="Access Denied — CampusConnect"), 403

    @app.errorhandler(404)
    def not_found_error(error):
        return render_template('errors/404.html', title="Page Not Found — CampusConnect"), 404

    @app.errorhandler(500)
    def internal_error(error):
        db.session.rollback()
        return render_template('errors/500.html', title="Server Error — CampusConnect"), 500

    # Context processors
    @app.context_processor
    def inject_global_vars():
        return {
            'current_year': datetime.now().year,
            'now': datetime.now()
        }

    # Register CLI commands
    register_cli_commands(app)

    # Ensure tables exist in app context
    with app.app_context():
        try:
            db.create_all()
        except Exception as e:
            app.logger.error(f"Error during db.create_all(): {e}")

    return app


def register_cli_commands(app):
    """Register custom Flask CLI management commands."""
    from app.models import User, Event, Registration

    @app.cli.command("init-db")
    def init_db():
        """Initialize all database tables."""
        db.create_all()
        click.echo("[OK] Database tables initialized successfully.")

    @app.cli.command("create-admin")
    @click.option('--email', prompt=True, help="Administrator email address")
    @click.option('--name', prompt=True, help="Administrator full name")
    @click.option('--password', prompt=True, hide_input=True, confirmation_prompt=True, help="Password")
    def create_admin(email, name, password):
        """Create or promote an administrator account."""
        clean_email = email.strip().lower()
        user = User.query.filter_by(email=clean_email).first()
        if user:
            user.role = 'ADMIN'
            user.full_name = name.strip()
            user.set_password(password)
            db.session.commit()
            click.echo(f"[OK] Existing user {clean_email} was promoted to ADMINISTRATOR.")
        else:
            admin = User(
                full_name=name.strip(),
                email=clean_email,
                role='ADMIN'
            )
            admin.set_password(password)
            db.session.add(admin)
            db.session.commit()
            click.echo(f"[OK] Administrator account '{clean_email}' created successfully.")

    @app.cli.command("seed-events")
    def seed_events():
        """Seed sample events for demonstration and testing."""
        # Find or create a default admin to assign as creator
        admin = User.query.filter_by(role='ADMIN').first()
        if not admin:
            admin = User(
                full_name="Admin Director",
                email="admin@campusconnect.edu",
                role='ADMIN'
            )
            admin.set_password("Admin@123")
            db.session.add(admin)
            db.session.commit()
            click.echo("[OK] Default admin account created: admin@campusconnect.edu (password: Admin@123)")

        today = date.today()

        sample_events = [
            {
                "title": "College Hackathon 2026",
                "category": "Technology",
                "description": "A 24-hour non-stop coding hackathon where student teams develop innovative software solutions for real-world campus and social problems. Prizes, mentorship, food, and swag provided!",
                "venue": "Computer Science Innovation Lab (Block B)",
                "event_date": today + timedelta(days=10),
                "start_time": time(9, 0),
                "capacity": 80
            },
            {
                "title": "Annual Cultural Fest — Euphoria",
                "category": "Cultural",
                "description": "The flagship annual cultural extravaganza featuring solo and group dance competitions, battle of the bands, drama performances, fashion showcase, and live acoustic night.",
                "venue": "University Main Amphitheatre",
                "event_date": today + timedelta(days=18),
                "start_time": time(17, 30),
                "capacity": 300
            },
            {
                "title": "Inter-College Sports Meet",
                "category": "Sports",
                "description": "Annual athletic championship featuring track and field events, 5v5 basketball, football tournament, badminton, and table tennis. Trophies and certificates for all finalists.",
                "venue": "Campus Sports Complex & Main Ground",
                "event_date": today + timedelta(days=25),
                "start_time": time(8, 0),
                "capacity": 150
            },
            {
                "title": "Web Development Workshop: Python & Modern Web",
                "category": "Workshop",
                "description": "Hands-on masterclass on building responsive, scalable full-stack web applications with Python, Flask, modern CSS architectures, and relational database systems.",
                "venue": "Seminar Hall 2 & Virtual Stream",
                "event_date": today + timedelta(days=7),
                "start_time": time(14, 0),
                "capacity": 60
            },
            {
                "title": "Technical Seminar: AI & Emerging Tech Trends",
                "category": "Seminar",
                "description": "Distinguished guest lecture with industry leaders discussing generative AI, cloud computing, cybersecurity paradigms, and career pathways for engineering students.",
                "venue": "Auditorium A (Admin Block)",
                "event_date": today + timedelta(days=14),
                "start_time": time(11, 0),
                "capacity": 120
            }
        ]

        added_count = 0
        for data in sample_events:
            existing = Event.query.filter_by(title=data["title"]).first()
            if not existing:
                event = Event(
                    title=data["title"],
                    category=data["category"],
                    description=data["description"],
                    venue=data["venue"],
                    event_date=data["event_date"],
                    start_time=data["start_time"],
                    capacity=data["capacity"],
                    created_by=admin.id
                )
                db.session.add(event)
                added_count += 1

        db.session.commit()
        click.echo(f"[OK] Seed complete: {added_count} new events added ({len(sample_events) - added_count} already existed).")
