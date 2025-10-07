from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import login_user, logout_user, login_required, current_user
from .models import db, User, Lecturer, Student
from flask_jwt_extended import create_access_token
import random
import string

auth_bp = Blueprint("auth_bp", __name__, template_folder="templates/auth")

def generate_employee_id():
    prefix = "DUT-L"
    suffix = ''.join(random.choices(string.digits, k=4))
    return f"{prefix}{suffix}"


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

        # -----------------------------
        # 1️⃣ Validate Input Fields
        # -----------------------------
        if not full_name or not email or not password:
            flash("All fields are required.", "warning")
            return redirect(url_for("auth_bp.lecturer_register"))

        # -----------------------------
        # 2️⃣ Check for Existing Account
        # -----------------------------
        existing_user = User.query.filter_by(email=email).first()
        if existing_user:
            flash("Email already exists. Please log in instead.", "danger")
            return redirect(url_for("auth_bp.lecturer_login"))

        # -----------------------------
        # 3️⃣ Create the User Record
        # -----------------------------
        password_hash = generate_password_hash(password)
        new_user = User(
            full_name=full_name,
            email=email,
            password_hash=password_hash,
            role="lecturer"
        )

        db.session.add(new_user)
        db.session.flush()  # assign an ID before linking to Lecturer

        # -----------------------------
        # 4️⃣ Create the Linked Lecturer Profile
        # -----------------------------
        employee_id = generate_employee_id()
        new_lecturer = Lecturer(
            id=new_user.id,            # link to User table
            employee_id=employee_id,   # auto-generated ID
        )

        db.session.add(new_lecturer)
        db.session.commit()

        # -----------------------------
        # 5️⃣ Success Message and Redirect
        # -----------------------------
        flash(f"Lecturer account created successfully! Your Employee ID is {employee_id}", "success")
        return redirect(url_for("auth_bp.lecturer_login"))

    # -----------------------------
    # 6️⃣ GET Request (Render Form)
    # -----------------------------
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


    user = User.query.filter_by(email=email).first()
    if not user or not check_password_hash(user.password_hash, password):
        return jsonify({"msg": "Invalid credentials"}), 401

    token = create_access_token(identity=user.id)
    return jsonify({
        "access_token": token,
        "user_id": user.id,
        "full_name": user.full_name
    })
