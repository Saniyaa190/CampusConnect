import os
from datetime import datetime, date, time, timedelta, timezone
import click
import pymysql
from flask import Flask, render_template
from app.extensions import db, migrate, login_manager, csrf
from config import config_by_name


import tempfile
import pathlib


def test_database_connectivity(uri, host='localhost', port=3306, user='root', password='', db_name='campusconnect'):
    """Test whether target database is reachable before initializing SQLAlchemy."""
    # If custom DATABASE_URL was provided, test that URI directly with short timeout
    if os.getenv('DATABASE_URL'):
        try:
            from sqlalchemy import create_engine, text
            connect_args = {'connect_timeout': 3} if 'mysql' in uri else {}
            engine = create_engine(uri, connect_args=connect_args)
            with engine.connect() as conn:
                conn.execute(text("SELECT 1"))
            engine.dispose()
            return True, "Connected successfully"
        except Exception as e:
            return False, str(e)

    # Standard local MySQL socket check
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


def seed_initial_data():
    """Seed initial administrator and sample events if database is empty."""
    from app.models import User, Event

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
    return added_count


def create_app(config_name='default'):
    """Application factory for CampusConnect."""
    base_dir = os.path.abspath(os.path.dirname(__file__))
    templates_dir = os.path.join(base_dir, 'templates')
    static_dir = os.path.join(base_dir, 'static')
    app = Flask(__name__, template_folder=templates_dir, static_folder=static_dir)

    # Load configuration
    config_obj = config_by_name.get(config_name, config_by_name['default'])
    app.config.from_object(config_obj)

    is_serverless = bool(os.getenv('VERCEL') or os.getenv('AWS_LAMBDA_FUNCTION_NAME'))

    # Ensure safe writable instance folder
    if is_serverless:
        app.instance_path = os.path.join(tempfile.gettempdir(), 'instance')

    try:
        os.makedirs(app.instance_path, exist_ok=True)
    except OSError:
        pass

    # Verify and configure database engine before initializing SQLAlchemy
    if not app.config.get('TESTING'):
        db_uri = app.config.get('SQLALCHEMY_DATABASE_URI', '')
        if db_uri.startswith('mysql'):
            host = app.config.get('DB_HOST', 'localhost')
            port = app.config.get('DB_PORT', 3306)
            user = app.config.get('DB_USERNAME', 'root')
            password = app.config.get('DB_PASSWORD', '')
            db_name = app.config.get('DB_NAME', 'campusconnect')

            can_connect, err_msg = test_database_connectivity(db_uri, host, port, user, password, db_name)
            if not can_connect:
                if app.config.get('ALLOW_SQLITE_FALLBACK', True) or is_serverless:
                    tmp_db = os.path.join(tempfile.gettempdir(), 'campusconnect.db')
                    sqlite_path = pathlib.Path(tmp_db).as_posix()

                    app.logger.warning(
                        f"MySQL connection unavailable ({err_msg}). Falling back to SQLite: {sqlite_path}"
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

    # Security response headers
    @app.after_request
    def set_security_headers(response):
        response.headers['X-Content-Type-Options'] = 'nosniff'
        response.headers['X-Frame-Options'] = 'SAMEORIGIN'
        response.headers['X-XSS-Protection'] = '1; mode=block'
        return response

    # Context processors
    @app.context_processor
    def inject_global_vars():
        return {
            'current_year': datetime.now().year,
            'now': datetime.now()
        }

    # Register CLI commands
    register_cli_commands(app)

    # Ensure tables exist and seed demo data if fresh database
    with app.app_context():
        try:
            db.create_all()
            from app.models import Event
            if Event.query.first() is None:
                seed_initial_data()
        except Exception as e:
            app.logger.error(f"Error during db initialization: {e}")

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
        added = seed_initial_data()
        click.echo(f"[OK] Seed complete: {added} new events created.")
