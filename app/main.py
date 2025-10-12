import os
from flask import Flask, Blueprint, render_template, redirect, url_for, flash, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_login import LoginManager, login_required, current_user
from datetime import datetime
from .models import (
    db,
    User,
    Student,
    Lecturer,
    Admin,
    Faculty,
    Department,
    Course,
    Module,
    LecturerAssignment,
    AttendanceSession,
    AttendanceRecord
)


# ----------------------------
# Initialize Flask extensions
# ----------------------------
migrate = Migrate()
login_manager = LoginManager()
login_manager.login_view = "main_bp.landing"

# ----------------------------
# Blueprint
# ----------------------------
main_bp = Blueprint("main_bp", __name__, template_folder="templates")

# ----------------------------
# Flask-Login loader
# ----------------------------
@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# ----------------------------
# Routes
# ----------------------------
@main_bp.route("/")
def landing():
    return render_template("landing.html")


# ----------------------------
# ADMIN DASHBOARD
# ----------------------------
@main_bp.route("/admin/dashboard")
@login_required
def admin_dashboard():
    if current_user.role != "admin":
        flash("Access denied. Admins only.", "danger")
        return redirect(url_for("main_bp.dashboard"))

    lecturers = (
        db.session.query(Lecturer, Department, Faculty)
        .join(Department, Lecturer.department_id == Department.id, isouter=True)
        .join(Faculty, Department.faculty_id == Faculty.id, isouter=True)
        .all()
    )

    faculties = Faculty.query.all()
    modules = Module.query.all()

    assignments = (
        db.session.query(LecturerAssignment)
        .join(Lecturer)
        .join(Faculty)
        .join(Department)
        .join(Course)
        .join(Module)
        .order_by(LecturerAssignment.assigned_at.desc())
        .all()
    )

    return render_template(
        "admin_dashboard.html",
        admin=current_user,
        lecturers=[l[0] for l in lecturers],
        faculties=faculties,
        modules=modules,
        assignments=assignments
    )


# ----------------------------
# ADMIN: Assign Lecturer to Module
# ----------------------------
@main_bp.route("/admin/assign_lecturer", methods=["POST"])
@login_required
def assign_lecturer():
    if current_user.role != "admin":
        flash("Access denied. Admins only.", "danger")
        return redirect(url_for("main_bp.admin_dashboard"))

    lecturer_id = request.form.get("lecturer_id")
    module_id = request.form.get("module_id")
    faculty_id = request.form.get("faculty_id")
    department_id = request.form.get("department_id")
    course_id = request.form.get("course_id")

    if not all([lecturer_id, module_id, faculty_id, department_id, course_id]):
        flash("All required fields must be selected.", "danger")
        return redirect(url_for("main_bp.admin_dashboard"))

    existing = LecturerAssignment.query.filter_by(
        lecturer_id=lecturer_id,
        module_id=module_id,
        course_id=course_id
    ).first()
    if existing:
        flash("This lecturer is already assigned to this module.", "warning")
        return redirect(url_for("main_bp.admin_dashboard"))

    new_assignment = LecturerAssignment(
        lecturer_id=lecturer_id,
        faculty_id=faculty_id,
        department_id=department_id,
        course_id=course_id,
        module_id=module_id,
        assigned_at=datetime.utcnow()
    )
    db.session.add(new_assignment)
    db.session.commit()

    flash("Lecturer successfully assigned to module!", "success")
    return redirect(url_for("main_bp.admin_dashboard"))


# ----------------------------
# LECTURER DASHBOARD
# ----------------------------
@main_bp.route("/dashboard")
@login_required
def dashboard():
    if current_user.role == "admin":
        return redirect(url_for("main_bp.admin_dashboard"))

    if current_user.role != "lecturer":
        flash("Access denied. Lecturers only.", "danger")
        return redirect(url_for("main_bp.landing"))

    lecturer = Lecturer.query.get(current_user.id)
    if not lecturer:
        flash("Lecturer profile not found.", "danger")
        return redirect(url_for("main_bp.landing"))

    assignments = LecturerAssignment.query.filter_by(lecturer_id=lecturer.id).all()
    module_ids = [a.module_id for a in assignments]

    # --- NEW LOGIC START ---
    # Get all courses related to the lecturer's assigned modules
    course_ids = (
        db.session.query(Module.course_id)
        .filter(Module.id.in_(module_ids))
        .distinct()
        .all()
    )
    course_ids = [c[0] for c in course_ids]

    # Fetch all students enrolled in those courses
    students = (
        Student.query
        .filter(Student.course_id.in_(course_ids))
        .join(User)
        .all()
    )
    # --- NEW LOGIC END ---


    attendance_records = (
        AttendanceRecord.query
        .join(Student)
        .filter(Student.module_id.in_(module_ids))
        .all()
    )

    print(students[0].user.full_name if students else "No students found")
    attendance_scores = {}
    for record in attendance_records:
        student_id = record.student_id
        if record.status == "present":
            attendance_scores[student_id] = attendance_scores.get(student_id, 0) + 10

    print(attendance_records)
    return render_template(
        "dashboard.html",
        lecturer=current_user,
        lecturer_profile=lecturer,
        assignments=assignments,
        students=students,
        attendance_records=attendance_records,
        attendance_scores=attendance_scores
    )



# ----------------------------
# LECTURER: Allocate Attendance Marks
# ----------------------------
@main_bp.route("/lecturer/allocate_marks", methods=["POST"])
@login_required
def allocate_marks():
    if current_user.role != "lecturer":
        flash("Access denied.", "danger")
        return redirect(url_for("main_bp.dashboard"))

    student_id = request.form.get("student_id")
    module_id = request.form.get("module_id")
    marks = int(request.form.get("marks", 0))

    if not student_id or not module_id:
        flash("Missing data. Please select a valid student and module.", "warning")
        return redirect(url_for("main_bp.dashboard"))

    student = Student.query.get(student_id)
    if not student:
        flash("Student not found.", "danger")
        return redirect(url_for("main_bp.dashboard"))

    # Check attendance session for the module
    record = AttendanceRecord.query.join(AttendanceSession)\
        .filter(AttendanceRecord.student_id == student_id,
                AttendanceSession.module_id == module_id)\
        .first()

    if not record:
        flash("No attendance record found for this student.", "warning")
        return redirect(url_for("main_bp.dashboard"))

    if record.status != "present":
        flash("Cannot allocate marks — student has not scanned their face.", "danger")
        return redirect(url_for("main_bp.dashboard"))

    record.attendance_marks = marks
    db.session.commit()

    flash(f"✅ {marks} marks allocated to {student.user.full_name}.", "success")
    return redirect(url_for("main_bp.dashboard"))


# ----------------------------
# ADMIN AJAX ENDPOINTS
# ----------------------------
@main_bp.route("/admin/get_departments/<int:faculty_id>")
@login_required
def get_departments(faculty_id):
    departments = Department.query.filter_by(faculty_id=faculty_id).all()
    return jsonify([{"id": d.id, "name": d.name} for d in departments])


@main_bp.route("/admin/get_courses/<int:faculty_id>/<int:department_id>")
@login_required
def get_courses(faculty_id, department_id):
    courses = Course.query.filter_by(department_id=department_id).all()
    return jsonify([{"id": c.id, "name": c.name} for c in courses])


@main_bp.route("/admin/get_modules/<int:course_id>")
@login_required
def get_modules(course_id):
    modules = Module.query.filter_by(course_id=course_id).all()
    return jsonify([{"id": m.id, "name": m.name} for m in modules])


# ----------------------------
# Flask App Factory
# ----------------------------
def create_app():
    app = Flask(__name__)
    app.config["SECRET_KEY"] = os.getenv("SECRET_KEY", "dev_secret_key")
    app.config["SQLALCHEMY_DATABASE_URI"] = os.getenv(
        "DATABASE_URL",
        "mysql+pymysql://root:Oct20ber2002@localhost/attendance_db"
    )
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

    db.init_app(app)
    migrate.init_app(app, db)
    login_manager.init_app(app)
    app.register_blueprint(main_bp)

    return app


# ----------------------------
# Run App
# ----------------------------
if __name__ == "__main__":
    app = create_app()
    app.run(debug=True)
