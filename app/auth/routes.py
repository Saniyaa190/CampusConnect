from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_user, logout_user, login_required, current_user
from app.extensions import db
from app.models import User
from app.forms import LoginForm, RegisterForm, ProfileForm
from app.utils import send_notification

auth_bp = Blueprint("auth", __name__)

@auth_bp.route("/login", methods=["GET", "POST"])
def login():
    if current_user.is_authenticated:
        if current_user.is_admin:
            return redirect(url_for("admin.dashboard"))
        elif current_user.is_organizer:
            return redirect(url_for("organizer.dashboard"))
        return redirect(url_for("student.dashboard"))

    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data.strip().lower()).first()
        if user and user.check_password(form.password.data):
            login_user(user, remember=form.remember.data)
            flash(f"Welcome back, {user.name}!", "success")
            
            next_page = request.args.get("next")
            if next_page and next_page.startswith("/"):
                return redirect(next_page)
            
            if user.is_admin:
                return redirect(url_for("admin.dashboard"))
            elif user.is_organizer:
                return redirect(url_for("organizer.dashboard"))
            else:
                return redirect(url_for("student.dashboard"))
        else:
            flash("Invalid email or password. Please try again.", "danger")

    return render_template("auth/login.html", form=form)


@auth_bp.route("/register", methods=["GET", "POST"])
def register():
    if current_user.is_authenticated:
        return redirect(url_for("index"))

    form = RegisterForm()
    if form.validate_on_submit():
        user = User(
            name=form.name.data.strip(),
            email=form.email.data.strip().lower(),
            role=form.role.data,
            department=form.department.data,
            year=form.year.data if form.role.data == "student" else "Faculty / Staff"
        )
        user.set_password(form.password.data)
        db.session.add(user)
        db.session.commit()

        # Send welcome notification
        send_notification(
            user.id,
            "Welcome to CampusConnect!",
            f"Hello {user.name}, your account as a {user.role.capitalize()} has been successfully created. Explore events and get involved!"
        )
        db.session.commit()

        flash("Registration successful! You can now log in.", "success")
        return redirect(url_for("auth.login"))

    return render_template("auth/register.html", form=form)


@auth_bp.route("/logout")
@login_required
def logout():
    logout_user()
    flash("You have been successfully logged out.", "info")
    return redirect(url_for("index"))


@auth_bp.route("/profile", methods=["GET", "POST"])
@login_required
def profile():
    form = ProfileForm(obj=current_user)
    if form.validate_on_submit():
        # Verify current password if user wants to change password
        if form.new_password.data:
            if not form.current_password.data or not current_user.check_password(form.current_password.data):
                flash("Current password is incorrect. Password was not changed.", "danger")
                return render_template("auth/profile.html", form=form)
            current_user.set_password(form.new_password.data)
            flash("Password updated successfully.", "info")

        current_user.name = form.name.data.strip()
        current_user.department = form.department.data
        if current_user.is_student:
            current_user.year = form.year.data

        db.session.commit()
        flash("Your profile has been updated.", "success")
        return redirect(url_for("auth.profile"))

    return render_template("auth/profile.html", form=form)
