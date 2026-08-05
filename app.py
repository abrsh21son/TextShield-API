from flask import Flask, flash, jsonify, make_response, redirect, render_template, request, session, url_for
from functools import wraps
import secrets

from sqlalchemy import and_
from sqlmodel import delete, func, select
from werkzeug.security import check_password_hash, generate_password_hash

import config
from routes.analyze import analyze_bp
from utility.database.main import get_session, init_db
from utility.database.model import APIKey, Admin, TextAnalysisRequest, UsageLog, User
from utility.mapper import map_logs_to_weekly_chart_data

app = Flask(__name__)
app.secret_key = config.FLASK_SECRET_KEY
app.register_blueprint(analyze_bp)

init_db()


def admin_required(f):  # protects admin-only routes
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if session.get("role") != "admin":
            flash("You do not have permission to access this page.", "error")
            return redirect(url_for("admin_login"))
        return f(*args, **kwargs)

    return decorated_function


def login_required(f):  # protects user-only routes
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if "user_id" not in session:
            flash("Please log in to access this page.", "warning")
            return redirect(url_for("user_login"))
        return f(*args, **kwargs)

    return decorated_function


@app.route("/")  # landing page
def home():
    return render_template("User/landing-page.html")


@app.route("/admindashboard")
@admin_required
def admindashboard():
    db = get_session()
    try:
        stats = {
            "total_users": db.exec(select(func.count(User.id))).one(),
            "api_requests": db.exec(select(func.count(TextAnalysisRequest.id))).one(),
            "toxic_blocked": db.exec(
                select(func.count(TextAnalysisRequest.id)).where(
                    TextAnalysisRequest.isprofane == True  # noqa: E712
                )
            ).one(),
            "active_api_keys": db.exec(
                select(func.count(APIKey.id)).where(APIKey.isactive == True)  # noqa: E712
            ).one(),
        }
        all_users = db.exec(select(User)).all()
        users_data = []
        for user in all_users:
            users_data.append(
                {
                    "email": user.email,
                    "status": getattr(user, "status", "approved"),
                    "credits": user.credits,
                    "api_requests": len(user.text_analysis_requests),
                    "joined": user.createdat.strftime("%Y-%m-%d"),
                }
            )
        return render_template("Admin/admin-dashboard.html", stats=stats, users=users_data)
    except Exception:
        flash("An error occurred while loading the dashboard data.", "error")
        return render_template("Admin/admin-dashboard.html", stats={}, users=[])
    finally:
        db.close()


@app.route("/api/generate-key", methods=["POST"])
@login_required
def generate_api_key():
    user_id = session.get("user_id")
    if not user_id:
        return jsonify({"error": "Authentication error: No user ID in session"}), 401

    db = get_session()
    try:
        new_key_string = f"safe_{secrets.token_hex(24)}"
        new_key = APIKey(userid=user_id, thekey=new_key_string)
        db.add(new_key)
        db.commit()
        db.refresh(new_key)
        return jsonify(
            {
                "success": True,
                "api_key": new_key_string,
                "message": "Key generated successfully",
            }
        )
    except Exception:
        db.rollback()
        return jsonify({"error": "An internal error occurred. Could not generate key."}), 500
    finally:
        db.close()


@app.route("/api/delete-key", methods=["DELETE"])
@login_required
def delete_api_key():
    user_id = session.get("user_id")
    if not user_id:
        return jsonify({"success": False, "error": "Unauthorized"}), 401

    data = request.get_json()
    if not data or "key" not in data:
        return jsonify({"success": False, "error": "Missing key parameter"}), 400

    db = get_session()
    try:
        key_exists = db.exec(
            select(APIKey).where(
                and_(APIKey.userid == user_id, APIKey.thekey == data["key"])
            )
        ).first()
        if not key_exists:
            return jsonify({"success": False, "error": "Key not found or access denied"}), 404

        db.exec(
            delete(APIKey).where(
                and_(APIKey.userid == user_id, APIKey.thekey == data["key"])
            )
        )
        db.commit()
        return jsonify({"success": True}), 200
    except Exception:
        db.rollback()
        return jsonify({"success": False, "error": "Database error"}), 500
    finally:
        db.close()


@app.route("/user/dashboard")
@login_required
def user_dashboard():
    current_user = session.get("email")
    user_id = session.get("user_id")
    if not current_user or not user_id:
        session.clear()
        flash("Your session has expired or the user was not found. Please log in again.", "error")
        return redirect(url_for("user_login"))

    db = get_session()
    try:
        user_keys = db.exec(select(APIKey.thekey).where(APIKey.userid == user_id)).all()
        credit_result = db.exec(select(User.credits).where(User.id == user_id)).first()
        usage = db.exec(select(UsageLog).where(UsageLog.userid == user_id)).all()
        textanalyzed = db.exec(
            select(TextAnalysisRequest).where(TextAnalysisRequest.userid == user_id)
        ).all()
        chart_data = map_logs_to_weekly_chart_data(usage_logs=usage)
        credit = credit_result if credit_result is not None else 0
        return render_template(
            "User/user-dashboard.html",
            user=current_user,
            data={"chart_data": chart_data},
            keys=user_keys,
            credit=credit,
            totalanalysis=len(textanalyzed),
            chart_data=chart_data,
        )
    except Exception:
        db.rollback()
        flash("A database error occurred while loading your dashboard. Please try again.", "error")
        return redirect(url_for("user_login"))
    finally:
        db.close()


@app.route("/user/signup", methods=["GET", "POST"])
def user_signup():
    if request.method == "POST":
        email = request.form.get("email")
        password = request.form.get("password")
        if not email or not password:
            flash("Email and password are required.", "warning")
            return redirect(url_for("user_signup"))

        db = get_session()
        try:
            if db.exec(select(User).where(User.email == email)).first():
                flash("An account with this email already exists.", "warning")
                return redirect(url_for("user_signup"))
            db.add(User(email=email, password_hash=generate_password_hash(password)))
            db.commit()
            flash("Signup successful! Please log in.", "success")
            return redirect(url_for("user_login"))
        finally:
            db.close()

    return render_template("User/user-registration.html")


@app.route("/user/login", methods=["GET", "POST"])
def user_login():
    if request.method == "POST":
        email = request.form.get("email")
        password = request.form.get("password")
        db = get_session()
        try:
            user = db.exec(select(User).where(User.email == email)).first()
            if user and check_password_hash(user.password_hash, password):
                session.clear()
                session["user_id"] = user.id
                session["email"] = user.email
                session["role"] = "user"
                return redirect(url_for("user_dashboard"))
            flash("Invalid email or password. please try again", "error")
        finally:
            db.close()
    return render_template("User/user-login.html")


@app.route("/admin/login", methods=["GET", "POST"])
def admin_login():
    if request.method == "POST":
        email = request.form.get("email")
        password = request.form.get("password")
        db = get_session()
        try:
            admin = db.exec(select(Admin).where(Admin.email == email)).first()
            if admin and check_password_hash(admin.password_hash, password):
                session.clear()
                session["user_id"] = admin.id
                session["email"] = admin.email
                session["role"] = "admin"
                return redirect(url_for("admindashboard"))
            flash("Invalid email or password. pls try again", "error")
        finally:
            db.close()
    return render_template("Admin/admin-login.html")


@app.route("/api/usage-stats", methods=["GET"])
@login_required
def get_usage_stats():
    user_id = session.get("user_id")
    if not user_id:
        return jsonify({"error": "Unauthorized"}), 401

    db = get_session()
    try:
        user = db.exec(select(User).where(User.id == user_id)).first()
        if not user:
            return jsonify({"error": "User not found"}), 404

        usage_logs = db.exec(select(UsageLog).where(UsageLog.userid == user_id)).all()
        total_analyzed = (
            db.exec(
                select(func.count(TextAnalysisRequest.id)).where(
                    TextAnalysisRequest.userid == user_id
                )
            ).first()
            or 0
        )
        chart_data = map_logs_to_weekly_chart_data(usage_logs=usage_logs)
        response = make_response(
            jsonify(
                {
                    "credits_remaining": user.credits,
                    "total_analyzed": total_analyzed,
                    "chart_data": chart_data,
                }
            )
        )
        response.headers["Cache-Control"] = "no-cache"
        return response
    except Exception:
        return jsonify({"error": "Internal server error"}), 500
    finally:
        db.close()


@app.route("/logout")
def logout():
    session.clear()
    flash("You have been successfully logged out.", "success")
    return redirect(url_for("user_login"))


if __name__ == "__main__":
    app.run()



