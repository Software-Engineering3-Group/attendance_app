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

# ----------------------
# API: Login Lecturer and Admin (Web)
# ----------------------
@auth_bp.route("/api/login", methods=["POST"])
def api_login():
    data = request.get_json() or {}
    email = data.get("email")
    password = data.get("password")

    user = User.query.filter_by(email=email).first()
    if not user or not check_password_hash(user.password_hash, password):
        return jsonify({"msg": "Invalid credentials"}), 401

    token = create_access_token(identity=user.id)
    return jsonify({
        "access_token": token,
        "user_id": user.id,
        "full_name": user.full_name,
        "type": user.type
    })


# ----------------------
# API: Student Registration (Mobile)
# ----------------------
@auth_bp.route("/api/students/register", methods=["POST"])
def api_student_register():
    data = request.get_json() or {}

    full_name = data.get("full_name")
    email = data.get("email")
    contact = data.get("contact")
    password = data.get("password")
    student_number = data.get("student_number")
    faculty_id = data.get("faculty_id")
    department_id = data.get("department_id")
    course_id = data.get("course_id")
    module_id = data.get("module_id")
    face_encoding = data.get("face_encoding") 

    if not full_name or not email or not password or not student_number:
        return jsonify({"msg": "Missing required fields"}), 400

    if User.query.filter_by(email=email).first():
        return jsonify({"msg": "Email already registered"}), 409

    hashed = generate_password_hash(password)
    user = User(
        full_name=full_name,
        email=email,
        contact=contact,
        password_hash=hashed,
        type="student"
    )
    db.session.add(user)
    db.session.flush()  # retrieve user.id before commit

    student = Student(
        id=user.id,
        student_number=student_number,
        faculty_id=faculty_id,
        department_id=department_id,
        course_id=course_id,
        module_id=module_id,
        face_encoding=face_encoding
    )
    db.session.add(student)
    db.session.commit()

    return jsonify({"msg": "Student registered successfully", "user_id": user.id}), 201


# ----------------------
# API: Student Login (Mobile)
# ----------------------
@auth_bp.route("/api/students/login", methods=["POST"])
def api_student_login():
    data = request.get_json() or {}
    email = data.get("email")
    password = data.get("password")


    user = User.query.filter_by(email=email).first()
    if not user or not check_password_hash(user.password_hash, password):
        return jsonify({"msg": "Invalid credentials"}), 401

    token = create_access_token(identity=user.id)
    return jsonify({
        "access_token": token,
        "user_id": user.id,
        "full_name": user.full_name
    })
# -------------------- AJAX: Departments by Faculty --------------------
@auth_bp.route("/get_departments/<int:faculty_id>")
def get_departments(faculty_id):
    """Return JSON list of departments for a selected faculty."""
    departments = Department.query.filter_by(faculty_id=faculty_id).all()
    return jsonify([{"id": d.id, "name": d.name} for d in departments])
