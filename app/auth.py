from flask import Blueprint, render_template, request, redirect, url_for, flash
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import login_user, logout_user, login_required, current_user
from .models import db, User

auth_bp = Blueprint("auth_bp", __name__, template_folder="templates/auth")

# -------------------- ADMIN REGISTRATION --------------------
@auth_bp.route("/admin/register", methods=["GET", "POST"])
def admin_register():
    """
    Admin registration (should be limited or done by super admin only)
    """
    if request.method == "POST":
        full_name = request.form.get("full_name")
        email = request.form.get("email")
        password = request.form.get("password")

        if not full_name or not email or not password:
            flash("All fields are required.", "warning")
            return redirect(url_for("auth_bp.admin_register"))

        existing_user = User.query.filter_by(email=email).first()
        if existing_user:
            flash("Email already exists. Please log in.", "danger")
            return redirect(url_for("auth_bp.admin_login"))

        password_hash = generate_password_hash(password)
        admin_user = User(full_name=full_name, email=email, password_hash=password_hash, role="admin")

        db.session.add(admin_user)
        db.session.commit()

        flash("Admin account created successfully!", "success")
        return redirect(url_for("auth_bp.admin_login"))

    return render_template("admin_register.html")


# -------------------- ADMIN LOGIN --------------------
@auth_bp.route("/admin/login", methods=["GET", "POST"])
def admin_login():
    """
    Admin login only
    """
    if request.method == "POST":
        email = request.form.get("email")
        password = request.form.get("password")

        admin = User.query.filter_by(email=email, role="admin").first()

        if not admin or not check_password_hash(admin.password_hash, password):
            flash("Invalid email or password.", "danger")
            return redirect(url_for("auth_bp.admin_login"))

        login_user(admin)
        flash(f"Welcome back, {admin.full_name}!", "success")
        return redirect(url_for("admin_bp.dashboard"))

    return render_template("admin_login.html")


# -------------------- LECTURER REGISTRATION --------------------
@auth_bp.route("/lecturer/register", methods=["GET", "POST"])
def lecturer_register():
    """
    Lecturer self-registration
    """
    if request.method == "POST":
        full_name = request.form.get("full_name")
        email = request.form.get("email")
        password = request.form.get("password")

        if not full_name or not email or not password:
            flash("All fields are required.", "warning")
            return redirect(url_for("auth_bp.lecturer_register"))

        existing_user = User.query.filter_by(email=email).first()
        if existing_user:
            flash("Email already exists. Please log in.", "danger")
            return redirect(url_for("auth_bp.lecturer_login"))

        password_hash = generate_password_hash(password)
        new_lecturer = User(full_name=full_name, email=email, password_hash=password_hash, role="lecturer")

        db.session.add(new_lecturer)
        db.session.commit()

        flash(f"Lecturer account created! Your Employee ID is {new_lecturer.employee_id}", "success")
        return redirect(url_for("auth_bp.lecturer_login"))

    return render_template("lecturer_register.html")


# -------------------- LECTURER LOGIN --------------------
@auth_bp.route("/lecturer/login", methods=["GET", "POST"])
def lecturer_login():
    """
    Lecturer login only
    """
    if request.method == "POST":
        email = request.form.get("email")
        password = request.form.get("password")

        lecturer = User.query.filter_by(email=email, role="lecturer").first()

        if not lecturer or not check_password_hash(lecturer.password_hash, password):
            flash("Invalid email or password.", "danger")
            return redirect(url_for("auth_bp.lecturer_login"))

        login_user(lecturer)
        flash(f"Welcome back, {lecturer.full_name}!", "success")
        return redirect(url_for("main_bp.dashboard"))

    return render_template("lecturer_login.html")


# -------------------- LOGOUT --------------------
@auth_bp.route("/logout")
@login_required
def logout():
    logout_user()
    flash("You have logged out successfully.", "info")
    return redirect(url_for("auth_bp.lecturer_login"))
