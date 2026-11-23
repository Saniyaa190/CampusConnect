import os
from flask import Flask, render_template, redirect, url_for
from config import Config
from app.extensions import db, login_manager, csrf

def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)

    # Initialize extensions
    db.init_app(app)
    login_manager.init_app(app)
    csrf.init_app(app)

    # Context processors
    @app.context_processor
    def inject_context():
        from flask_login import current_user
        unread_count = 0
        if current_user.is_authenticated:
            unread_count = current_user.unread_notifications_count
        return dict(
            unread_notifications_count=unread_count,
            app_name="CampusConnect",
            tagline="Your Campus. Your Events. Your Community."
        )

    # Register blueprints
    from app.auth.routes import auth_bp
    from app.student.routes import student_bp
    from app.organizer.routes import organizer_bp
    from app.admin.routes import admin_bp
    from app.events.routes import events_bp
    from app.notifications.routes import notifications_bp

    app.register_blueprint(auth_bp, url_prefix="/auth")
    app.register_blueprint(student_bp, url_prefix="/student")
    app.register_blueprint(organizer_bp, url_prefix="/organizer")
    app.register_blueprint(admin_bp, url_prefix="/admin")
    app.register_blueprint(events_bp, url_prefix="/events")
    app.register_blueprint(notifications_bp, url_prefix="/notifications")

    # Main landing page route
    @app.route("/")
    def index():
        from app.models import Event, User, Registration
        from datetime import date
        
        # Featured upcoming events (approved and future)
        upcoming_events = Event.query.filter(
            Event.approval_status == "approved",
            Event.event_date >= date.today()
        ).order_by(Event.event_date.asc(), Event.start_time.asc()).limit(6).all()
        
        # Platform statistics
        total_events = Event.query.filter_by(approval_status="approved").count()
        total_students = User.query.filter_by(role="student").count()
        total_organizers = User.query.filter_by(role="organizer").count()
        total_registrations = Registration.query.filter_by(registration_status="confirmed").count()

        return render_template(
            "landing.html",
            upcoming_events=upcoming_events,
            total_events=total_events,
            total_students=total_students,
            total_organizers=total_organizers,
            total_registrations=total_registrations
        )

    # Error handlers
    @app.errorhandler(403)
    def forbidden_error(error):
        return render_template("errors/403.html"), 403

    @app.errorhandler(404)
    def not_found_error(error):
        return render_template("errors/404.html"), 404

    @app.errorhandler(500)
    def internal_error(error):
        db.session.rollback()
        return render_template("errors/500.html"), 500

    return app
