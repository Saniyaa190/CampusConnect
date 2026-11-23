import os
import uuid
from functools import wraps
from werkzeug.utils import secure_filename
from flask import abort, flash, redirect, url_for, current_app
from flask_login import current_user
from app.extensions import db
from app.models import Notification

def role_required(*roles):
    """Decorator to enforce role-based access control."""
    def decorator(fn):
        @wraps(fn)
        def decorated_view(*args, **kwargs):
            if not current_user.is_authenticated:
                flash("Please log in to view this page.", "warning")
                return redirect(url_for("auth.login"))
            if current_user.role not in roles:
                flash("Access denied: You do not have permission to view this page.", "danger")
                if current_user.role == "admin":
                    return redirect(url_for("admin.dashboard"))
                elif current_user.role == "organizer":
                    return redirect(url_for("organizer.dashboard"))
                else:
                    return redirect(url_for("student.dashboard"))
            return fn(*args, **kwargs)
        return decorated_view
    return decorator

def student_required(fn):
    return role_required("student")(fn)

def organizer_required(fn):
    return role_required("organizer")(fn)

def admin_required(fn):
    return role_required("admin")(fn)

def allowed_file(filename):
    """Check if uploaded file has an allowed image extension."""
    if "." not in filename:
        return False
    ext = filename.rsplit(".", 1)[1].lower()
    return ext in current_app.config.get("ALLOWED_EXTENSIONS", {"png", "jpg", "jpeg", "webp", "gif"})

def save_cover_image(file_storage):
    """Safely save uploaded cover image with a unique filename."""
    if not file_storage or not hasattr(file_storage, "filename") or not file_storage.filename:
        return None
    if not allowed_file(file_storage.filename):
        return False
    
    ext = file_storage.filename.rsplit(".", 1)[1].lower()
    unique_filename = f"event_{uuid.uuid4().hex[:12]}.{ext}"
    upload_folder = current_app.config["UPLOAD_FOLDER"]
    os.makedirs(upload_folder, exist_ok=True)
    file_path = os.path.join(upload_folder, unique_filename)
    file_storage.save(file_path)
    return unique_filename

def send_notification(user_id, title, message):
    """Create in-app notification for a user."""
    notification = Notification(
        user_id=user_id,
        title=title,
        message=message
    )
    db.session.add(notification)
    return notification
