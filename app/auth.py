from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import login_user, logout_user, login_required
from .models import db, User, Lecturer, Faculty, Department
import random
import string

# -------------------- Blueprint --------------------
auth_bp = Blueprint("auth_bp", __name__, template_folder="templates/auth")

# -------------------- Helper --------------------
def generate_employee_id(prefix="DUT-L"):
    """Generate a random employee ID."""
    suffix = ''.join(random.choices(string.digits, k=4))
    return f"{prefix}{suffix}"

# -------------------- ADMIN ROUTES --------------------
@auth_bp.route("/admin/register", methods=["GET", "POST"])
def admin_register():
    if request.method == "POST":
        full_name = request.form.get("full_name")
        email = request.form.get("email")
        password = request.form.get("password")

        if not all([full_name, email, password]):
            flash("All fields are required.", "warning")
            return redirect(url_for("auth_bp.admin_register"))

        if User.query.filter_by(email=email).first():
            flash("Email already exists.", "danger")
            return redirect(url_for("auth_bp.admin_login"))

        user = User(
            full_name=full_name,
            email=email,
            password_hash=generate_password_hash(password),
            role="admin"
        )
        db.session.add(user)
        db.session.commit()

        flash("Admin registered successfully!", "success")
        return redirect(url_for("auth_bp.admin_login"))

    return render_template("admin_register.html")

@auth_bp.route("/admin/login", methods=["GET", "POST"])
def admin_login():
    if request.method == "POST":
        email = request.form.get("email")
        password = request.form.get("password")

        admin = User.query.filter_by(email=email, role="admin").first()
        if not admin or not check_password_hash(admin.password_hash, password):
            flash("Invalid email or password.", "danger")
            return redirect(url_for("auth_bp.admin_login"))

        login_user(admin)
        flash(f"Welcome back, {admin.full_name}!", "success")
        return redirect(url_for("main_bp.admin_dashboard"))

    return render_template("admin_login.html")

# -------------------- LECTURER ROUTES --------------------
@auth_bp.route("/lecturer/register", methods=["GET", "POST"])
def lecturer_register():
    """Register a new lecturer and link to faculty/department."""
    faculties = Faculty.query.all()

    if request.method == "POST":
        full_name = request.form.get("full_name")
        email = request.form.get("email")
        password = request.form.get("password")
        faculty_id = request.form.get("faculty_id")
        department_id = request.form.get("department_id")

        if not all([full_name, email, password, faculty_id, department_id]):
            flash("All fields are required.", "warning")
            return redirect(url_for("auth_bp.lecturer_register"))

        if User.query.filter_by(email=email).first():
            flash("Email already registered.", "danger")
            return redirect(url_for("auth_bp.lecturer_register"))

        # Create User
        user = User(
            full_name=full_name,
            email=email,
            password_hash=generate_password_hash(password),
            role="lecturer"
        )
        db.session.add(user)
        db.session.commit()

        # Create Lecturer profile linked to User
        lecturer = Lecturer(
            id=user.id,
            employee_id=generate_employee_id(),
            faculty_id=faculty_id,
            department_id=department_id
        )
        db.session.add(lecturer)
        db.session.commit()

        flash("Lecturer registered successfully!", "success")
        return redirect(url_for("auth_bp.lecturer_login"))

    return render_template("lecturer_register.html", faculties=faculties)

@auth_bp.route("/lecturer/login", methods=["GET", "POST"])
def lecturer_login():
    if request.method == "POST":
        email = request.form.get("email")
        password = request.form.get("password")

        lecturer_user = User.query.filter_by(email=email, role="lecturer").first()
        if not lecturer_user or not check_password_hash(lecturer_user.password_hash, password):
            flash("Invalid email or password.", "danger")
            return redirect(url_for("auth_bp.lecturer_login"))

        login_user(lecturer_user)
        flash(f"Welcome back, {lecturer_user.full_name}!", "success")
        return redirect(url_for("main_bp.dashboard"))

    return render_template("lecturer_login.html")

# -------------------- LOGOUT --------------------
@auth_bp.route("/logout")
@login_required
def logout():
    logout_user()
    flash("Logged out successfully.", "info")
    return redirect(url_for("auth_bp.admin_login"))

# -------------------- AJAX: Departments by Faculty --------------------
@auth_bp.route("/get_departments/<int:faculty_id>")
def get_departments(faculty_id):
    """Return JSON list of departments for a selected faculty."""
    departments = Department.query.filter_by(faculty_id=faculty_id).all()
    return jsonify([{"id": d.id, "name": d.name} for d in departments])
