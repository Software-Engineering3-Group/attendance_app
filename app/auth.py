from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import login_user, logout_user, login_required
from flask_jwt_extended import create_access_token
from .models import db, User, Faculty, Department, Course, Module, Student, Lecturer

auth_bp = Blueprint("auth_bp", __name__)

# ----------------------
# Lecturer Registration (Web)
# ----------------------
@auth_bp.route("/register", methods=["GET", "POST"])
def register():
    faculties = Faculty.query.order_by(Faculty.name).all()

    if request.method == "POST":
        full_name = request.form.get("full_name")
        email = request.form.get("email")
        contact = request.form.get("contact")
        password = request.form.get("password")
        password2 = request.form.get("password2")
        department_id = request.form.get("department") or None  # only department is needed

        # --- Validations ---
        if not full_name or not email or not password:
            flash("Please fill in all required fields.", "danger")
            return redirect(url_for("auth_bp.register"))

        if password != password2:
            flash("Passwords do not match.", "danger")
            return redirect(url_for("auth_bp.register"))

        if User.query.filter_by(email=email).first():
            flash("Email already registered.", "warning")
            return redirect(url_for("auth_bp.register"))

        # --- Create User ---
        hashed = generate_password_hash(password)
        user = User(
            full_name=full_name,
            email=email,
            contact=contact,
            password_hash=hashed,
            type="lecturer"
        )
        db.session.add(user)
        db.session.flush()  # get user.id

        # --- Create Lecturer (fixed) ---
        lecturer = Lecturer(
            id=user.id,
            lecturer_id=f"L-{user.id:04d}",
            department_id=department_id
        )
        db.session.add(lecturer)
        db.session.commit()

        flash("Account created successfully — please log in.", "success")
        return redirect(url_for("auth_bp.login"))

    return render_template("register.html", faculties=faculties)



# ----------------------
# Web Login
# ----------------------
@auth_bp.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form.get("email")
        password = request.form.get("password")

        user = User.query.filter_by(email=email).first()
        if not user or not check_password_hash(user.password_hash, password):
            flash("Invalid email or password.", "danger")
            return redirect(url_for("auth_bp.login"))

        login_user(user)
        flash("Logged in successfully.", "success")
        return redirect(url_for("main_bp.dashboard"))

    return render_template("login.html")


# ----------------------
# Logout
# ----------------------
@auth_bp.route("/logout")
@login_required
def logout():
    logout_user()
    flash("Logged out successfully.", "info")
    return redirect(url_for("auth_bp.login"))


# ----------------------
# API: Login (Mobile - Any User)
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
    face_encoding = data.get("face_encoding")  # optional field

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

    user = User.query.filter_by(email=email, type="student").first()
    if not user or not check_password_hash(user.password_hash, password):
        return jsonify({"msg": "Invalid credentials"}), 401

    token = create_access_token(identity=user.id)
    return jsonify({
        "access_token": token,
        "user_id": user.id,
        "full_name": user.full_name
    })
