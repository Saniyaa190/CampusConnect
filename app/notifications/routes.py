from flask import Blueprint, render_template, redirect, url_for, flash, request, abort
from flask_login import login_required, current_user
from sqlalchemy import desc
from app.extensions import db
from app.models import Notification

notifications_bp = Blueprint("notifications", __name__)

@notifications_bp.route("/")
@login_required
def index():
    notifications = Notification.query.filter_by(user_id=current_user.id)\
        .order_by(desc(Notification.created_at)).all()
    return render_template("notifications/index.html", notifications=notifications)


@notifications_bp.route("/<int:notification_id>/read", methods=["POST"])
@login_required
def mark_read(notification_id):
    notification = db.session.get(Notification, notification_id)
    if not notification or notification.user_id != current_user.id:
        abort(404)

    notification.is_read = True
    db.session.commit()
    return redirect(request.referrer or url_for("notifications.index"))


@notifications_bp.route("/mark-all-read", methods=["POST"])
@login_required
def mark_all_read():
    Notification.query.filter_by(user_id=current_user.id, is_read=False).update({"is_read": True})
    db.session.commit()
    flash("All notifications marked as read.", "success")
    return redirect(request.referrer or url_for("notifications.index"))
