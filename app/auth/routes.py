from urllib.parse import urlsplit
from flask import render_template, redirect, url_for, flash, request
from flask_login import login_user, logout_user, current_user, login_required
from app.auth import auth_bp
from app.extensions import db
from app.models import User
from app.forms import LoginForm, SignupForm


def is_safe_url(target):
    """Ensure redirect URL belongs to this domain and is safe to prevent open redirects."""
    if not target:
        return False
    ref_url = urlsplit(request.host_url)
    test_url = urlsplit(target)

    # If an absolute URL with scheme is provided, verify scheme and host match
    if test_url.scheme:
        return test_url.scheme in ('http', 'https') and ref_url.netloc == test_url.netloc

    # Relative path validation: must start with single '/', avoid protocol-relative '//', and prevent backslashes
    return target.startswith('/') and not target.startswith('//') and '\\' not in target


@auth_bp.route('/signup', methods=['GET', 'POST'])
def signup():
    """Student account registration."""
    if current_user.is_authenticated:
        return redirect(url_for('student.dashboard' if current_user.is_student else 'admin.dashboard'))

    form = SignupForm()
    if form.validate_on_submit():
        user = User(
            full_name=form.full_name.data.strip(),
            email=form.email.data.strip().lower(),
            role='STUDENT'
        )
        user.set_password(form.password.data)
        db.session.add(user)
        db.session.commit()

        flash("Account created successfully! Please sign in with your credentials.", "success")
        return redirect(url_for('auth.login'))

    return render_template('signup.html', form=form, title="Sign Up — CampusConnect")


@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    """User authentication for Students and Administrators."""
    if current_user.is_authenticated:
        return redirect(url_for('student.dashboard' if current_user.is_student else 'admin.dashboard'))

    form = LoginForm()
    if form.validate_on_submit():
        email = form.email.data.strip().lower()
        user = User.query.filter_by(email=email).first()

        if user and user.check_password(form.password.data):
            login_user(user, remember=form.remember_me.data)
            flash(f"Welcome back, {user.full_name}!", "success")

            next_page = request.args.get('next')
            if next_page and is_safe_url(next_page):
                return redirect(next_page)

            if user.is_admin:
                return redirect(url_for('admin.dashboard'))
            return redirect(url_for('student.dashboard'))
        else:
            flash("Invalid email or password. Please verify your credentials and try again.", "danger")

    return render_template('login.html', form=form, title="Sign In — CampusConnect")


@auth_bp.route('/logout')
@login_required
def logout():
    """Log out authenticated user."""
    logout_user()
    flash("You have been signed out successfully.", "info")
    return redirect(url_for('main.home'))
