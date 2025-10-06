from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import login_user, logout_user, login_required, current_user
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity
from .models import db, User, Department, Course, Module, Student

auth_bp = Blueprint("auth_bp", __name__)

@auth_bp.route("/register", methods=["GET", "POST"])
def register():
    # show dept list
    try:
        departments = Department.query.order_by(Department.name).all()
    except Exception:
        departments = []

    if request.method == "POST":
        full_name = request.form.get("full_name")
        email = request.form.get("email")
        contact = request.form.get("contact")
        password = request.form.get("password")
        password2 = request.form.get("password2")
        department_id = request.form.get("department") or None
        course_id = request.form.get("course") or None
        module_id = request.form.get("module") or None

        if not full_name or not email or not password:
            flash("Please fill required fields", "danger")
            return redirect(url_for("auth_bp.register"))

        if password != password2:
            flash("Passwords do not match", "danger")
            return redirect(url_for("auth_bp.register"))

        if User.query.filter_by(email=email).first():
            flash("Email already registered", "warning")
            return redirect(url_for("auth_bp.register"))

        hashed = generate_password_hash(password)
        user = User(
            full_name=full_name, email=email, contact=contact,
            password_hash=hashed, role="lecturer",
            department_id=department_id, course_id=course_id, module_id=module_id
        )
        db.session.add(user)
        db.session.commit()
        flash("Account created — please log in", "success")
        return redirect(url_for("auth_bp.login"))

    return render_template("register.html", departments=departments)

@auth_bp.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form.get("email")
        password = request.form.get("password")
        user = User.query.filter_by(email=email).first()
        if not user or not check_password_hash(user.password_hash, password):
            flash("Invalid credentials", "danger")
            return redirect(url_for("auth_bp.login"))
        login_user(user)
        flash("Logged in", "success")
        return redirect(url_for("main_bp.dashboard"))
    return render_template("login.html")

@auth_bp.route("/logout")
@login_required
def logout():
    logout_user()
    flash("Logged out", "info")
    return redirect(url_for("auth_bp.login"))

# Mobile API login (returns JWT)
@auth_bp.route("/api/login", methods=["POST"])
def api_login():
    data = request.get_json() or {}
    email = data.get("email")
    password = data.get("password")
    user = User.query.filter_by(email=email).first()
    if not user or not check_password_hash(user.password_hash, password):
        return jsonify({"msg": "Bad credentials"}), 401
    token = create_access_token(identity=user.id)
    return jsonify({"access_token": token})

# endpoints for dynamic selects
@auth_bp.route("/api/departments/<int:dept_id>/courses")
def api_courses(dept_id):
    courses = Course.query.filter_by(department_id=dept_id).order_by(Course.name).all()
    return jsonify([{"id": c.id, "name": c.name} for c in courses])

@auth_bp.route("/api/courses/<int:course_id>/modules")
def api_modules(course_id):
    modules = Module.query.filter_by(course_id=course_id).order_by(Module.name).all()
    return jsonify([{"id": m.id, "name": m.name} for m in modules])

# -------------- Student registration (mobile)
@auth_bp.route("/api/students/register", methods=["POST"])
def api_student_register():
    data = request.get_json() or {}
    print(data)

    full_name = data.get("full_name")
    email = data.get("email")
    contact = data.get("contact")
    password = data.get("password")
    student_number = data.get("student_number")
    department_id = data.get("department_id")
    course_id = data.get("course_id")
    module_id = data.get("module_id")
    # Optional: face encoding
    face_encoding = data.get("face_encoding")

    if not full_name or not email or not password or not student_number:
        return jsonify({"msg": "Required fields missing"}), 400

    if User.query.filter_by(email=email).first():
        return jsonify({"msg": "Email already registered"}), 409

    # Create user
    hashed = generate_password_hash(password)
    user = User(
        full_name=full_name,
        email=email,
        contact=contact,
        password_hash=hashed,
        type="student",
    )
    db.session.add(user)
    db.session.flush()  # Get the user.id before commit

    # Create student profile
    student = Student(
        id=user.id,
        student_number=student_number,
        department_id=department_id,
        course_id=course_id,
        module_id=module_id,
        face_encoding=face_encoding  # If you want to store it (add column first)
    )
    db.session.add(student)

    # If you want to store face_encoding, add column first
    # Example: db.Column(db.Text, nullable=True) in Student

    db.session.commit()

    return jsonify({"msg": "Student registered successfully"}), 201

# ----------------------
# Student login (mobile)
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
    return jsonify({"access_token": token, "user_id": user.id, "full_name": user.full_name})